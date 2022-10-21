from typing import Any

from pydantic import BaseModel


class GeneralResponse(BaseModel):
    code: int
    message: str
    data: Any = None


class SuccessResponse(GeneralResponse):
    code = 0
    message = "success"


class ErrorResponse(GeneralResponse):
    code = 1
    message = "error"
