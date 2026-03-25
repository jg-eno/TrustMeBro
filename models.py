from pydantic import BaseModel

class Eval(BaseModel):
    api_url: str

class Response(BaseModel):
    pass