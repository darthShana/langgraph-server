from typing import List

from langchain_community.tools import TavilySearchResults
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field


tool = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
    # include_domains=[...],
    # exclude_domains=[...],
    # name="...",            # overwrite default tool name
    # description="...",     # overwrite default tool description
    # args_schema=...,       # overwrite default args_schema: BaseModel
)


class OnlineReviewsInput(BaseModel):
    vehicles: str = Field(description="the vehicle description to get online reviews for")


def online_review(vehicles: str):
    return tool.invoke({'query': "find feedback about this vehicle from other experts and consumers?"})


online_reviews_tool = StructuredTool.from_function(
    func=online_review,
    name="online_review",
    description="""
        Useful for searching for online reviews about a vehicle
        """,
    args_schema=OnlineReviewsInput,
)