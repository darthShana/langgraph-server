from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class RequestCallbackInput(BaseModel):
    suitable_time: str = Field(description="the date and time the customer wished to do the test drive")
    phone_number: str = Field(description="users phone number where the human sales person can reach them")
    email: str = Field(description="users email address where the human sales person can reach them")


def request_callback(suitable_time: str, phone_number: str, email: str):
    return True


request_callback_tool = StructuredTool.from_function(
    func=request_callback,
    name="request_callback",
    description="""
        Useful to request a human sales rep to call back the users
        """,
    args_schema=RequestCallbackInput,
)