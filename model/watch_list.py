from typing import List

from pydantic.v1 import BaseModel, Field


class Comment(BaseModel):
    vehicles: str = Field("vehicle source this comment is for")
    comment: str = Field("the comment")


class WatchList(BaseModel):
    user_id: str = Field("Unique identifier for this user this watch list belongs to")
    vehicles: List[str] = Field("List of vehicle sources that are on this watch list")
    comments: List[Comment] = Field("List of vehicle sources that are on this watch list")