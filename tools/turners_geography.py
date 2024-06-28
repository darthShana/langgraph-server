from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
from tinydb import TinyDB, Query

db = TinyDB('db/user.json')


class TurnersGeographyInput(BaseModel):
    location: str = Field(description="the location the human is looking for a vehicle in")


def turners_geography(location: str) -> list[str]:
    if location.casefold() == 'Auckland'.casefold():
        locations = ['Westgate', 'North Shore', 'Otahuhu', 'Penrose', 'Botany', 'Manukau']
    elif location.casefold() == 'Wellington'.casefold():
        locations = ['Wellington', 'Porirua']
    else:
        locations = [location]

    return locations


turners_geography_tool = StructuredTool.from_function(
    func=turners_geography,
    name="turners_locations",
    description="""
        Fetch the turners branches for a given location. This tool will find the relevant turners branches for that location, 
        so it can be used in subsequent actions to find vehicles. do NOT call this tool if a location isn't mentioned. Do NOT guess
        Example:
        if the chat history contains "im in rotorua" then call the tool with "rotorua"
        if the chat history contains "im near christchurch" then call the tool with "christchurch"
        """,
    args_schema=TurnersGeographyInput,
)