import os

from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


class OnlineReviewsInput(BaseModel):
    vehicles: str = Field(description="the vehicle description to get online reviews for")


def online_review(vehicles: str):
    return tavily_client.search("find feedback about this vehicle from other experts and consumers: "+vehicles)


online_reviews_tool = StructuredTool.from_function(
    func=online_review,
    name="online_review",
    description="""
        Useful for searching for online reviews about a vehicle
        """,
    args_schema=OnlineReviewsInput,
)