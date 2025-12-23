from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PromptExecutionError(BaseModel):
    """Represents an error that occurred during LLM execution with associated context."""
    error_message: str
    prompt: Optional[str] = None
    response_text: Optional[str] = None
    error_type: str = Field(default="unknown")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ExecutionMetadata(BaseModel):
    """Metadata about an LLM execution."""
    cost: float
    duration_seconds: float
    errors: List[PromptExecutionError] = Field(default_factory=list)
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    prompt: Optional[str] = None
    response_text: Optional[str] = None
