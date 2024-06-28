from typing import List

from pydantic.v1 import BaseModel, Field

from model.vehicle_listing import LocationEnum


class UserProfile(BaseModel):
    id: str = Field("Unique identifier for this user")
    name: str = Field("The name the the user would like to be called")
    preferred_branches: List[LocationEnum] = Field("List of branches the user is looking for a vehicle in")