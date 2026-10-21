"""Chat HTTP routes — authenticated product advisor."""

from fastapi import APIRouter

from core.deps import CurrentUserDep, DbDep
from core.rate_limit import ChatRateLimitDep
from core.responses import success
from modules.chat.schema import ChatRequest, ChatResponse
from modules.chat.service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
def chat(
    payload: ChatRequest,
    db: DbDep,
    _current_user: CurrentUserDep,
    _rate_limit: ChatRateLimitDep,
):
    history = [item.model_dump() for item in payload.history]
    result = ChatService(db).chat(message=payload.message, history=history)
    body = ChatResponse(
        reply=result["reply"],
        tools_used=result["tools_used"],
    )
    return success(
        message="Chat response generated",
        result=body.model_dump(mode="json"),
    )
