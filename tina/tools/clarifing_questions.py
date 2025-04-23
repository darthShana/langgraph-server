import logging
from enum import Enum
from typing import List

from langchain.chat_models import init_chat_model
from langchain_core.prompts import FewShotPromptWithTemplates, PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from tina.retrievers.query_extractor import QueryExtractor
from tina.retrievers.utils import escape_examples
from tina.tools.templates import clarifying_question_prefix, clarifying_question_examples, \
    clarifying_question_example_template


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

llm = init_chat_model("gpt-4o", model_provider="openai")

class QuestionType(str, Enum):
    multi_choice = 'MultiChoice'
    true_false = 'True/False'
    freeform = 'freeform'

class ClarifyingQuestionResult(BaseModel):
    question: str = Field(description="")
    question_type: QuestionType = Field(description="")
    options: List[str] = Field(description="")

prefix = PromptTemplate(
            input_variables=["metadata"], template=clarifying_question_prefix
        )

suffix = PromptTemplate(
    input_variables=["chat_history"],
    template="""
                    So given 
                    chat_history: 
                    {{chat_history}}.
                    Suggest a clarifying question
                    """,
)

CLARIFYING_QUESTION_EXAMPLE_PROMPT = PromptTemplate(
        input_variables=["chat_history", "result"], template=clarifying_question_example_template
    )


def clarifying_question(chat_history: List[str]):
    prompt = FewShotPromptWithTemplates(
        suffix=suffix,
        prefix=prefix,
        input_variables=["metadata", "chat_history"],
        examples=escape_examples(clarifying_question_examples),
        example_prompt=CLARIFYING_QUESTION_EXAMPLE_PROMPT,
        example_separator="\n",
    )

    structured_llm = llm.with_structured_output(ClarifyingQuestionResult)
    chain = prompt | structured_llm
    response: dict | ClarifyingQuestionResult = chain.invoke({'metadata': QueryExtractor().metadata_field_info, 'chat_history': chat_history})
    log.info(f'response: {response}')
    return response.model_dump()


clarifying_question_tool_name = 'ClarifyingQuestion'
clarifying_question_tool = StructuredTool.from_function(
    func=clarifying_question,
    name=clarifying_question_tool_name,
    description="""
    Useful for getting clarifying questions from a user who is looking for a vehicle
    """
)

if __name__ == '__main__':
    # clarifying_question([])
    clarifying_question([
        "ai: Can you share the top feature you prioritize in a vehicle?",
        "human: id like to get something more recent and more fuel efficient than i had before",
        "ai: May I know your preference for the vehicle's fuel type?"
        "human: hybrid"
    ])