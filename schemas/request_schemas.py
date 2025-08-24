from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str

class QueryRequest(BaseModel):
    latex: str
    query: str
