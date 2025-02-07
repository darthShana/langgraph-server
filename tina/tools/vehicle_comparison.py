import logging
import os
from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from langchain_core.utils.json import parse_json_markdown
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from tinydb import Query, TinyDB
from tavily import TavilyClient

from tina.tools.templates import custom_comparison_template

log = logging.getLogger(__name__)
db = TinyDB('db/db.json')
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
chat = ChatOpenAI(model="gpt-4o")



class VehicleQuery(BaseModel):
    vehicle_source: str = Field(description="the source url of the vehicle to compare")
    vehicle_description: str = Field(description="a description of the vehicle to compare, include its make model year and variant")


class VehicleComparisonInput(BaseModel):
    vehicles: List[VehicleQuery] = Field(description="list of vehicles to compare")


class VehicleDetails(BaseModel):
    image_url: str = Field(description="image of the vehicle")
    manufacturer_details: str = Field(description="manufacturer details about the vehicle. Its make, model, year and variant")
    features: str = Field(description="the features of the vehicle")
    condition: str = Field(description="the condition of the vehicle")
    reviews: str = Field(description="reviews about the vehicle")


class VehicleComparisonOutput(BaseModel):
    vehicle: List[VehicleDetails] = Field(description="list if vehicle details from the comparison")


def vehicle_comparison(vehicles: List[VehicleQuery]):

    q = Query()
    load_candidates = [db.search(q.source == v.vehicle_source)[0] for v in vehicles]
    load_reviews = [
        tavily_client.search("find feedback about this vehicle from other experts and consumers: "+v.vehicle_description)
        for v in vehicles]

    for (load_candidate, load_review) in zip(load_candidates, load_reviews):
        load_candidate['reviews'] = load_review

    parser = JsonOutputParser(pydantic_object=VehicleComparisonOutput)
    prompt = PromptTemplate(
        template=custom_comparison_template,
        input_variables=["vehicles"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | chat
    res = chain.invoke({
        "vehicles": load_candidates
    })
    log.info(res.content)
    return parse_json_markdown(res.content)


vehicle_comparison_tool = StructuredTool.from_function(
    func=vehicle_comparison,
    name="vehicle_comparison",
    description="""
        Useful for comparing multiple vehicles
        """,
    args_schema=VehicleComparisonInput,
)
