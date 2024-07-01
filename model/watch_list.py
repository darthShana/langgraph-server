from pydantic.v1 import BaseModel, Field


class WatchList(BaseModel):
    user_id: str = Field("Unique identifier for this user this watch list belongs to")
    vehicles: list[str] = Field("List of vehicle sources that are on this watch list")
    comments: dict[str, str] = Field("List of vehicle sources that are on this watch list")