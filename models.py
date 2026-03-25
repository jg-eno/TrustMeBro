from typing import Literal

from pydantic import BaseModel, Field


class MMLUChoice(BaseModel):
    """JSON-schema structured output: exactly one of A–D."""

    letter: Literal["A", "B", "C", "D"] = Field(
        description="The letter of the correct multiple-choice answer."
    )


class Eval(BaseModel):
    api_url: str
    model_name: str
    use_structured_output: bool = True


class Response(BaseModel):
    accuracy: float = Field(ge=0, le=100, description="Percent correct (0–100).")
    correct: int
    total: int
    details: list[dict]
