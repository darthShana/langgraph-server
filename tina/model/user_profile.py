from typing import List
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    user_id: str = Field("Unique identifier for this user")
    name: str = Field("The name the the user would like to be called")
