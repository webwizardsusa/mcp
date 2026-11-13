"""Chat agent: provider tool-calling over ProductAdvisorTools (MCP tool set)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from services.product_advisor.tools import ProductAdvisorTools
from services.providers import get_ai_provider


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.tools = ProductAdvisorTools(db)

    def chat(self, message: str, history: list[dict]) -> dict:
        if get_ai_provider() == "gemini":
            from services.providers.gemini.chat_agent import run_chat
        else:
            from services.providers.openai.chat_agent import run_chat
        return run_chat(self.tools, message, history)
