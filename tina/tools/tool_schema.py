from datetime import time, date
from typing import List
from pydantic import BaseModel, Field


class VehicleSearchResult(BaseModel):
    source: str = Field(description="the source URL of the listing")
    image: str = Field(description="the image URL of the listing")
    listing_details: list[str] = Field(description="some details about the listing to feature")


class VehicleSearchResults(BaseModel):
    results: List[VehicleSearchResult] = Field(description="list of matching vehicle listings")
    comments: str = Field(description="some comments about the search results")


class Appointment(BaseModel):
    start_time: time = Field(description="the start time of the appointment")
    end_time: time = Field(description="the end time of the appointment")


class DailyAppointments(BaseModel):
    appointment_date: date = Field(description="the date these appointments are for")
    appointments: List[Appointment] = Field(description="the appointments available on this date")


class AvailableAppointments(BaseModel):
    days: List[DailyAppointments] = Field(description="the available appointments grouped by date")


