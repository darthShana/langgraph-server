import json

from langchain_core.runnables import ensure_config
from langchain_core.tools import StructuredTool
from tinydb import TinyDB, Query

from model.user_profile import UserProfile
import logging
log = logging.getLogger(__name__)
db = TinyDB('db/user.json')


def fetch_user_information() -> UserProfile:
    config = ensure_config()
    configuration = config.get("configurable", {})
    user_id = configuration.get("user_id", None)
    if not user_id:
        raise ValueError("No user ID configured")

    query = Query()
    user = db.search(query.id == user_id)
    if len(user)>0:
        return UserProfile(**user[0])
    else:
        profile = UserProfile(
            id=user_id,
            name="",
            preferred_branches=[]
        )
        db.insert(profile.dict())
        return profile


fetch_user_information_tool = StructuredTool.from_function(
    func=fetch_user_information,
    name="fetch_user_information",
    description="""
        Fetches known information about a user including what locations they are looking for vehicles in
        """,
)
