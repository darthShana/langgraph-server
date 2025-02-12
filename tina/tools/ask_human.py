from enum import Enum
from typing import List

from pydantic import BaseModel, Field

class AnswerType(str, Enum):
    datetime = 'datetime'
    text = 'text'


class Question(BaseModel):
    question: str = Field(description="the question to ask")
    answer_type: AnswerType = Field(description="the type od answer to the question being asked")

class AskHuman(BaseModel):
    questions: List[Question] = Field(description='the questions to ask')