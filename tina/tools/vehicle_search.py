import os
from typing import List, Optional

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from langchain_core.utils.json import parse_json_markdown
from langchain_openai import ChatOpenAI
from tinydb import TinyDB, Query
from tina.retrievers.query_extractor import QueryExtractor
from pinecone import Pinecone
from pydantic import BaseModel, Field

import voyageai
import logging

from tina.tools.templates import custom_stuff_template

from tina.tools.tool_schema import VehicleSearchResults

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
db = TinyDB('db/db.json')
vo = voyageai.Client()
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENVIRONMENT_REGION"])
index = pc.Index("turners-sample-stock")


query_extractor = QueryExtractor()
chat = init_chat_model("gpt-4o", model_provider="openai")


class VehicleSearchInput(BaseModel):
    chat_history: List[str] = Field(description="the chat history between an ai and human looking for a suitable vehicle")
    turners_locations: List[str] = Field(description="a list of turners branches where the human is looking for a vehicle.")


def vehicle_search(chat_history: List[str], turners_locations: List[str]) -> str:
    if turners_locations is None:
        turners_locations = []
    if len(turners_locations) > 0:
        chat_history.append(f"ai:the relevant Turners locations to search are {','.join(turners_locations)}")

    query = query_extractor.extract_query(chat_history)
    log.info(f"query: {query}")
    if query is None or len(query) == 0:
        query = "any car"

    vector = vo.embed([query['query']], model="voyage-large-2", input_type="document").embeddings[0]
    res = index.query(
        vector=vector,
        filter=query['filter'],
        top_k=5,
        include_metadata=True
    )
    sources = set(map(lambda x: x['metadata']['source'], res['matches']))
    log.info(f"results: {sources}")

    q = Query()
    load_candidates = [db.search(q.source == src)[0] for src in sources]

    prompt = PromptTemplate(
        template=custom_stuff_template,
        input_variables=["conversation", "vehicle_descriptions"],
    )
    structured_llm = chat.with_structured_output(VehicleSearchResults)
    chain = prompt | structured_llm
    response: dict | VehicleSearchResults = chain.invoke({
        "conversation": chat_history,
        "vehicle_descriptions": load_candidates
    })
    log.info(response)
    return response.model_dump()


vehicle_search_tool = StructuredTool.from_function(
    func=vehicle_search,
    name="vehicle_search",
    description="""
        Useful for finding suitable vehicles that are available based on a chat history between an AI and human.
        """,
    args_schema=VehicleSearchInput,
)

if __name__ == '__main__':
    conv = [
        "system:You are a helpful but sassy sales assistant, working for Turners Automotive Group",
        "ai:Hi! im Tina, a virtual sales assistant. How can i help you today?",
        "human:i want a new car",
        "ai:Awesome, you have come to the right place, could you tell me more about the kind od car your looking for?",
        "human:im in auckland, i need something with ISOFIX for my kids child seat",
        "ai:how about the budget you are working with?",
        "human:under 15k",
    ]
    vehicle_search(conv, ['Westgate', 'North Shore', 'Otahuhu', 'Penrose', 'Botany', 'Manukau'])

