import asyncio
from openai import AsyncOpenAI
from app.config import Settings
from app.schemas import SupportRequest, SupportResponse
def detect_category(message: str) -> str:
    normalized = message.lower()
    if any(word in normalized for word in ("refund", "payment", "charged")):
        return "billing"
    if any(word in normalized for word in ("order", "delivery", "shipping")):
        return "shipping"
    if any(word in normalized for word in ("error", "broken", "login")):
        return "technical"
    return "general"
async def create_mock_response(
    request: SupportRequest,
) -> SupportResponse:
    await asyncio.sleep(0.25)
    return SupportResponse(
        category=detect_category(request.message),
        priority=request.priority,
        suggested_reply=(
            "Thank you for contacting our support team. "
            "We have received your request and will review it shortly."
        ),
        processing_mode="mock",
    )
async def create_openai_response(
    request: SupportRequest,
    settings: Settings,
) -> SupportResponse:
    if not settings.openai_api_key:
        return await create_mock_response(request)
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=30.0,
        max_retries=2,
    )
    response = await client.responses.create(
        model=settings.openai_model,
        instructions=(
            "You are a professional customer support assistant. "
            "Write a concise, calm and helpful response. "
            "Do not promise refunds, shipping dates, or resolutions "
            "that have not been confirmed."
        ),
        input=(
            f"Customer message:\n{request.message}\n\n"
            f"Initial priority: {request.priority}\n\n"
            "Return only the suggested customer-facing reply."
        ),
        max_output_tokens=250,
    )
    suggested_reply = response.output_text.strip()
    if not suggested_reply:
        suggested_reply = (
            "Thank you for contacting our support team. "
            "We are reviewing your request."
        )
    return SupportResponse(
        category=detect_category(request.message),
        priority=request.priority,
        suggested_reply=suggested_reply,
        processing_mode="openai",
    )