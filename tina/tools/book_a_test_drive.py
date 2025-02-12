from typing import List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class BookATestDriveInput(BaseModel):
    sources: List[str] = Field("the source url of the vehicle to be be test driven")
    suitable_time: str = Field(description="the date and time the customer wished to do the test drive")
    phone: str = Field(description="phone number of the customer")
    email: str = Field(description="email address of the customer")


def book_a_test_drive(sources: List[str], booking_time: str, phone: str, email: str):
    return True


book_a_test_drive_tool = StructuredTool.from_function(
    func=book_a_test_drive,
    name="book_a_test_drive",
    description="""
        Useful for booking a test drive for vehicles
        """,
    args_schema=BookATestDriveInput,
)