"""Gemini generate_content with catalog tool calling (google-genai SDK)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from core.config import settings
from services.product_advisor.openai_bridge import OPENAI_TOOLS, dispatch_tool
from services.product_advisor.tools import ProductAdvisorTools

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are AI Product Advisor for an automotive spare parts catalog.
Prices are in USD. Use tools to look up real products before recommending.
Be concise, helpful, and explain why a product fits (vehicle, budget, use case, rating).
If tools return no products, say so and suggest a broader search.
Never invent product ids, prices, or stock that tools did not return.
When comparing, use clear bullet points."""

MAX_TOOL_ROUNDS = 5
# Transient capacity spikes are common on Gemini flash models.
GENERATE_RETRIES = 3
RETRY_BACKOFF_SECONDS = (0.8, 1.6, 3.2)


def _gemini_tools() -> list[types.Tool]:
    declarations: list[types.FunctionDeclaration] = []
    for entry in OPENAI_TOOLS:
        fn = entry.get("function") or {}
        name = fn.get("name")
        if not name:
            continue
        declarations.append(
            types.FunctionDeclaration(
                name=name,
                description=fn.get("description") or "",
                parameters_json_schema=fn.get("parameters") or {"type": "object"},
            )
        )
    return [types.Tool(function_declarations=declarations)]


def _history_contents(history: list[dict], message: str) -> list[types.Content]:
    contents: list[types.Content] = []
    for item in history[-12:]:
        role = item.get("role")
        text = (item.get("content") or "").strip()
        if not text:
            continue
        if role == "user":
            contents.append(
                types.Content(role="user", parts=[types.Part.from_text(text=text)])
            )
        elif role == "assistant":
            contents.append(
                types.Content(role="model", parts=[types.Part.from_text(text=text)])
            )
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message.strip())],
        )
    )
    return contents


def _function_calls(response: Any) -> list[Any]:
    calls = getattr(response, "function_calls", None) or []
    if calls:
        return list(calls)
    # Fallback: walk candidate parts
    try:
        parts = response.candidates[0].content.parts or []
    except (AttributeError, IndexError, TypeError):
        return []
    found = []
    for part in parts:
        fc = getattr(part, "function_call", None)
        if fc and getattr(fc, "name", None):
            found.append(fc)
    return found


def _response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    try:
        parts = response.candidates[0].content.parts or []
    except (AttributeError, IndexError, TypeError):
        return ""
    chunks: list[str] = []
    for part in parts:
        t = getattr(part, "text", None)
        if t:
            chunks.append(t)
    return "".join(chunks).strip()


def _is_transient_capacity_error(exc: BaseException) -> bool:
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    if code in {429, 503}:
        return True
    text = str(exc).lower()
    return "high demand" in text or "unavailable" in text or "resource_exhausted" in text


def _generate_with_retry(
    client: genai.Client,
    *,
    model: str,
    contents: list[types.Content],
    config: types.GenerateContentConfig,
) -> Any:
    last_exc: BaseException | None = None
    for attempt in range(GENERATE_RETRIES):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except (ClientError, ServerError) as exc:
            last_exc = exc
            if not _is_transient_capacity_error(exc) or attempt >= GENERATE_RETRIES - 1:
                raise
            delay = RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)]
            logger.warning(
                "Gemini capacity error on %s (attempt %s/%s); retrying in %.1fs: %s",
                model,
                attempt + 1,
                GENERATE_RETRIES,
                delay,
                exc,
            )
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def run_chat(tools: ProductAdvisorTools, message: str, history: list[dict]) -> dict:
    api_key = settings.gemini_api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY is not configured",
        )

    client = genai.Client(api_key=api_key)
    gemini_tools = _gemini_tools()
    contents = _history_contents(history, message)
    tools_used: list[str] = []

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=gemini_tools,
        temperature=0.3,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    try:
        for _ in range(MAX_TOOL_ROUNDS):
            response = _generate_with_retry(
                client,
                model=settings.GEMINI_CHAT_MODEL,
                contents=contents,
                config=config,
            )

            calls = _function_calls(response)
            if not calls:
                reply = _response_text(response)
                if not reply:
                    reply = (
                        "I could not generate a recommendation. Please try rephrasing."
                    )
                return {"reply": reply, "tools_used": tools_used}

            model_content = None
            try:
                model_content = response.candidates[0].content
            except (AttributeError, IndexError, TypeError):
                model_content = None
            if model_content is not None:
                contents.append(model_content)

            response_parts: list[types.Part] = []
            for call in calls:
                name = getattr(call, "name", None) or ""
                raw_args = getattr(call, "args", None) or {}
                args = dict(raw_args) if isinstance(raw_args, dict) else {}
                tools_used.append(name)
                try:
                    result = dispatch_tool(tools, name, args)
                except Exception:
                    logger.exception("Tool failed: %s", name)
                    result = {"error": f"Tool {name} failed"}

                # SDK expects a JSON-serializable mapping for function responses.
                if not isinstance(result, dict):
                    result = {"result": result}
                response_parts.append(
                    types.Part.from_function_response(
                        name=name,
                        response=json.loads(json.dumps(result, default=str)),
                    )
                )

            # Gemini expects function responses as user-role content (not "tool").
            contents.append(types.Content(role="user", parts=response_parts))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Gemini chat failed")
        if _is_transient_capacity_error(exc):
            detail = (
                "Gemini is busy right now (high demand). "
                "Please try again in a moment, or set GEMINI_CHAT_MODEL to "
                "gemini-3.1-flash-lite / gemini-flash-lite-latest."
            )
        else:
            detail = f"Gemini chat failed: {exc}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        ) from exc

    return {
        "reply": (
            "I looked up products but could not finish the answer in time. "
            "Please try a shorter question."
        ),
        "tools_used": tools_used,
    }
