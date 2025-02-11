import logging
import os
import requests
from dataclasses import dataclass
from typing import List
from math import radians, sin, cos, sqrt, atan2
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from tinydb import TinyDB
from pydantic import BaseModel, Field


log = logging.getLogger(__name__)
db = TinyDB('db/user.json')
API_KEY = os.environ["GOOGLE_API_KEY"]

@dataclass
class TurnersLocation:
    name: str
    place_id: str
    lat: float = None
    lng: float = None

turners_locations = [
    TurnersLocation("Whangarei", "ChIJ78PKBpF_C20RfpuC-APsyOQ", -35.72785760000001, 174.3174743),
    TurnersLocation("Westgate", "ChIJ8VthVocVDW0RZlEmxsQFWDQ", -36.8133642, 174.5982985),
    TurnersLocation("North Shore", "ChIJ5QDhLBY5DW0RpN1-oxvF6jU", -36.78159469999999, 174.7387267),
    TurnersLocation("Otahuhu", "ChIJjy_eGklPDW0R36XU6jQ40DE", -36.9353754, 174.8359329),
    TurnersLocation("Penrose", "ChIJsW3Tl_9JDW0R1EUZebXpT64", -36.9232054, 174.8308598),
    TurnersLocation("Botany", "ChIJAcZtXglLDW0R1ingXWQc7BI", -36.9275797, 174.8986172),
    TurnersLocation("Manukau", "ChIJF0KPOLlNDW0RcIiSemD8wrE", -36.9811325, 174.8780199),
    TurnersLocation("Avalon Drive", "ChIJtZJqBkYibW0RPeFKZTdshIk", -37.771588, 175.241755),
    TurnersLocation("Te Rapa Road", "ChIJHRaXk9gjbW0R2kIVS7nsxeQ", -37.7491149, 175.2369995),
    TurnersLocation("Tauranga", "ChIJNf8OrjXZbW0RCYtBwUkNn9s", -37.65466899999999, 176.194621),
    TurnersLocation("New Plymouth", "ChIJ4xSoq-tRFG0Rd_z1U6zhwE4", -39.04653220000001, 174.1171492),
    TurnersLocation("Napier", "ChIJ9w4QRi-zaW0R4pkHj-sTcj4", -39.48771920000001, 176.8903531),
    TurnersLocation("Rotorua", "ChIJQWuHh14nbG0RYj0lqC7UWyQ", -38.1213113, 176.2286733),
    TurnersLocation("Palmerston North", "ChIJ7cM3bNJMQG0RIkz2VM8Mo4Q", -40.33851, 175.59865),
    TurnersLocation("Porirua", "ChIJxQ4nMzuqOG0RigCkGXr8uz0", -41.1356877, 174.8335961),
    TurnersLocation("Nelson", "ChIJ_QoDmG_tO20RP6x2lQ9Ykdk", -41.276371, 173.2740325),
    TurnersLocation("Christchurch", "ChIJJ2IFdWOKMW0Rzj6DUgarHCM", -43.5404835, 172.610001),
    TurnersLocation("Timaru", "ChIJyd5-V8TrLG0RZDnoJPtGCiw", -44.3567299, 171.2389725),
    TurnersLocation("Dunedin", "ChIJAdB74h-sLqgRlpj0jEfplo0", -45.869141, 170.5209478),
    TurnersLocation("Invercargill", "ChIJ-4BdwFXD0qkRoGTJ5ro7ZRk", -46.38866520000001, 168.3470581),
]


def get_location_details(place_id: str) -> tuple:
    """Get latitude and longitude for a place ID using Google Places API"""
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "geometry",
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        result = response.json()
        if result.get("result") and result["result"].get("geometry"):
            location = result["result"]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None


class TurnersGeographyInput(BaseModel):
    config: RunnableConfig = Field(description="runnable config")
    distance: int = Field(description="max allowed distance to search for turners branches")


def turners_geography(config: RunnableConfig, distance: int) -> list[str] | None:
    log.info("in here turners Geography")
    lat = config.get("configurable", {}).get("latitude")
    lng = config.get("configurable", {}).get("longitude")
    log.info(f"getting turners locations for lat:{lat}, long:{lng}")

    for location in turners_locations:
        if location.lat is None or location.lng is None:
            location.lat, location.lng = get_location_details(location.place_id)
            print(f"{location.name}, lat:{location.lat}, lng:{location.lng}")

    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        _distance = R * c

        return _distance

    # Filter locations within radius
    nearby_locations = [
        location.name for location in turners_locations
        if location.lat is not None
        and location.lng is not None
        and calculate_distance(lat, lng, location.lat, location.lng) <= distance
    ]

    return nearby_locations


turners_geography_tool = StructuredTool.from_function(
    func=turners_geography,
    name="turners_geography",
    description="""
        Used to the turners branches near a user which can be used in subsequent tools to find vehicles. from the context
        do not ask the user for the distance to use just try 5, 10, 20km to return more branched if needed.
        """,
    args_schema=TurnersGeographyInput,
)

if __name__ == "__main__":
    # -36.907474353046766, 174.79087999884032
    nearby_locations = turners_geography({"configurable": {
        "latitude": -36.907474353046766,
        "longitude": 174.79087999884032
    }}, [], 10)

    print(nearby_locations)
