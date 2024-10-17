import json
import logging
import math
import os

import requests
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from tinydb import TinyDB, Query
from pydantic import BaseModel, Field


log = logging.getLogger(__name__)
db = TinyDB('db/user.json')
API_KEY = os.environ["GOOGLE_API_KEY"]

excluded_branches = [
    "Turners Cars Penrose Gavin Street (CashNow Bookings Only)",
    "Turners Service Centre",
    "Turners Automotive Group"
]


def create_viewport(latitude, longitude, distance_km):
    # Earth's radius in kilometers
    earth_radius = 6371

    # Convert latitude and longitude to radians
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)

    # Angular distance in radians on a great circle
    angular_distance = distance_km / earth_radius

    # Calculate the change in latitude
    delta_lat = angular_distance

    # Calculate the change in longitude
    delta_lon = math.asin(math.sin(angular_distance) / math.cos(lat_rad))

    # Calculate the coordinates of the viewport
    min_lat = latitude - math.degrees(delta_lat)
    max_lat = latitude + math.degrees(delta_lat)
    min_lon = longitude - math.degrees(delta_lon)
    max_lon = longitude + math.degrees(delta_lon)

    # Create the viewport dictionary
    viewport = {
        "low": {
            "latitude": min_lat,
            "longitude": min_lon
        },
        "high": {
            "latitude": max_lat,
            "longitude": max_lon
        }
    }

    return viewport


class TurnersGeographyInput(BaseModel):
    distance: int = Field(description="return branches that are less than this distance away, Try with a distance of 5km, 10km then 20km to find suitable turners branches when looking for suitable vehicles")


def turners_geography(config: RunnableConfig, distance: int) -> list[str] | None:
    log.info("in here turners Geography")
    lat = config.get("configurable", {}).get("latitude")
    long = config.get("configurable", {}).get("longitude")
    log.info(f"getting turners locations for lat:{lat}, long:{long}")

    url = 'https://places.googleapis.com/v1/places:searchText'

    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'places.id,places.displayName'
    }

    payload = {
        "textQuery": "Turners Cars",
        "locationRestriction": {
            "rectangle": create_viewport(lat, long, distance)
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    log.info(response.json())

    if 'places' in response.json():
        return [place['displayName']['text'] for place in response.json()['places'] if place['displayName']['text'] not in excluded_branches]
    else:
        return None


turners_geography_tool = StructuredTool.from_function(
    func=turners_geography,
    name="turners_locations",
    description="""
        Get the turners branches which can be used in subsequent actions to find vehicles.
        """,
    args_schema=TurnersGeographyInput,
)

if __name__ == "__main__":
    turners_geography({}, 10)
