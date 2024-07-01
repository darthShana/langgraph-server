from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
from tinydb import TinyDB, Query

from model.watch_list import WatchList

db = TinyDB('watch_list.json')


class AddToWatchListInput(BaseModel):
    user_id: str = Field("user id of the the user this watch list belongs to"),
    source: str = Field("the source url of the vehicle to be added to this watch list")


def add_to_watch_list(user_id: str, source: str):
    Q = Query()
    result = db.search(Q.user_id == user_id)
    if len(result) > 0:
        w = WatchList(**result[0])
    else:
        w = WatchList(user_id=user_id, source=[], comments={})
        db.insert(w.dict())

    w.vehicles.append(source)
    db.update(w.dict(), Q.user_id == user_id)


class GetWatchListInput(BaseModel):
    user_id: str = Field("user id of the the user this watch list")


def get_watch_list(user_id: str) -> Optional[WatchList]:
    Q = Query()
    result = db.search(Q.user_id == user_id)
    if len(result) > 0:
        return WatchList(**result[0])


add_to_watch_list_tool = StructuredTool.from_function(
    func=add_to_watch_list,
    name="add_to_watch_list",
    description="""
        Useful for adding a vehicle to a users watch list.
        """,
    args_schema=AddToWatchListInput
)

get_watch_list_tool = StructuredTool.from_function(
    func=get_watch_list,
    name="get_watch_list_tool",
    description="""
            Useful for getting a user's watch list
            """,
    args_schema=GetWatchListInput
)
