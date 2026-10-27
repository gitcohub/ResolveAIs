from typing import Literal
from pydantic import BaseModel, Field
SupportCategory = Literal["billing", "shipping", "technical", "general"]
SupportPriority = Literal["low", "normal", "high"]
class SupportRequest(BaseModel):
    message: str = Field(
        min_length=5,
        max_length=2000,
        description="The customer's support message.",
        examples=["My order has not arrived and I need an update."],
    )
    priority: SupportPriority = Field(
        default="normal",
        description="The initial priority assigned by the support team.",
    )
class SupportResponse(BaseModel):
    category: SupportCategory
    priority: SupportPriority
    suggested_reply: str
    processing_mode: Literal["mock", "openai"]

JobStatus = Literal["queued", "processing", "completed", "failed"]
class JobAcceptedResponse(BaseModel):
    job_id: str
    status: JobStatus
    status_url: str
class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: SupportResponse | None = None
    error: str | None = None