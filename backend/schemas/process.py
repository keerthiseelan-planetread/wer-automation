from pydantic import BaseModel


class ProcessRequest(BaseModel):
    year: int
    month: int
    language: str


class ProcessResponse(BaseModel):
    status: str
    message: str
