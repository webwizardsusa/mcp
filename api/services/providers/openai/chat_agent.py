"""OpenAI chat completions with catalog tool calling."""

from __future__ import annotations

import json
import logging

from fastapi import HTTPException, status
from openai import OpenAI

from core.config import settings
from services.product_advisor.openai_bridge import (
    OPENAI_TOOLS,
    dispatch_tool,
    parse_tool_arguments,
)
from services.product_advisor.tools import ProductAdvisorTools

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are AI Product Advisor for an automotive spare parts catalog.
Prices are in USD. Use tools to look up real products before recommending.
Be concise, helpful, and explain why a product fits (vehicle, budget, use case, rating).
If tools return no products, say so and suggest a broader search.
Never invent product ids, prices, or stock that tools did not return.
When comparing, use clear bullet points."""

MAX_TOOL_ROUNDS = 5


def run_chat(tools: ProductAdvisorTools, message: str, history: list[dict]) -> dict:
    api_key = settings.openai_api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured",
        )

    client = OpenAI(api_key=api_key)
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    for item in history[-12:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message.strip()})

    tools_used: list[str] = []

    try:
        for _ in range(MAX_TOOL_ROUNDS):
            response = client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=messages,
                tools=OPENAI_TOOLS,
                tool_choice="auto",
                temperature=0.3,
            )
            choice = response.choices[0]
            assistant_message = choice.message

            tool_calls = assistant_message.tool_calls or []
            if not tool_calls:
                reply = (assistant_message.content or "").strip()
                if not reply:
                    reply = (
                        "I could not generate a recommendation. Please try rephrasing."
                    )
                return {"reply": reply, "tools_used": tools_used}

            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments or "{}",
                            },
                        }
                        for call in tool_calls
                    ],
                }
            )

            for call in tool_calls:
                name = call.function.name
                args = parse_tool_arguments(call.function.arguments)
                tools_used.append(name)
                try:
                    result = dispatch_tool(tools, name, args)
                except Exception:
                    logger.exception("Tool failed: %s", name)
                    result = {"error": f"Tool {name} failed"}

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, default=str),
                    }
                )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("OpenAI chat failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI chat failed: {exc}",
        ) from exc

    return {
        "reply": (
            "I looked up products but could not finish the answer in time. "
            "Please try a shorter question."
        ),
        "tools_used": tools_used,
    }
