import uuid
from typing import Optional, List
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
from tinydb import TinyDB, Query

from model.watch_list import WatchList

watchlist_db = TinyDB('db/watch_list.json')
vehicle_db = TinyDB('db/db.json')


class AddToWatchListInput(BaseModel):
    user_id: str = Field("user id of the the user this watch list belongs to")
    sources: List[str] = Field("the source url of the vehicle to be added to this watch list")


def add_to_watch_list(user_id: str, sources: List[str]) -> None:
    Q = Query()
    result = watchlist_db.search(Q.user_id == user_id)
    if len(result) > 0:
        w = WatchList(**result[0])
    else:
        w = WatchList(user_id=user_id, vehicles=[], comments=[])
        watchlist_db.insert(w.dict())

    for source in sources:
        w.vehicles.append(source)

    watchlist_db.update(w.dict(), Q.user_id == user_id)


class GetWatchListInput(BaseModel):
    user_id: str = Field("user id of the the user this watch list")


def get_watch_list(user_id: str) -> Optional[dict]:
    Q = Query()
    result = watchlist_db.search(Q.user_id == user_id)
    if len(result) > 0:
        result_dict = WatchList(**result[0]).dict()
        vehicle_details = {}
        for v in result_dict['vehicles']:
            vehicle_details = vehicle_db.search(Q.source == v)
            vehicle_details[v] = vehicle_details

        result_dict['vehicle_details'] = vehicle_details
        return result_dict


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

if __name__ == "__main__":
    user_id = str(uuid.uuid4())
    add_to_watch_list(user_id, "https://www.turners.co.nz//Cars/Used-Cars-for-Sale/skoda/scala/25666306")
    print(get_watch_list(user_id))