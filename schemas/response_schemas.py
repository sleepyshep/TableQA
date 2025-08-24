from pydantic import BaseModel

class LatexResponse(BaseModel):
    text: str
    image: str
    # markdown: str

class AnswerResponse(BaseModel):
    think: str
    answer: str
