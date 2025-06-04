import json
import logging
from typing import Annotated, Optional

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query, where

from tina.tools.tool_schema import VehicleSearchResults

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
db = TinyDB('db/db.json')
llm = init_chat_model("gpt-4o", model_provider="openai")


class StructuredSearchInput(BaseModel):
    selected_vehicle_type: Optional[str] = Field("selected_vehicle_type")
    selected_make: Optional[str] = Field("selected_make")
    selected_model: Optional[str] = Field("selected_model")
    selected_year_from: Optional[str] = Field("selected_year_from")
    selected_year_to: Optional[str] = Field("selected_year_to")
    selected_kms_from: Optional[str] = Field("selected_kms_from")
    selected_kms_to: Optional[str] = Field("selected_kms_to")
    selected_price_from: Optional[str] = Field("selected_price_to")
    selected_price_to: Optional[str] = Field("selected_price_to")

def structured_search_options():

    Listing = Query()
    listings = db.search((Listing.metadata.exists()))

    vehicle_type_to_makes = {}
    make_to_models = {}
    vehicle_types = set()
    makes = set()
    models = set()

    for listing in listings:
        vehicle_type = listing['metadata']['vehicle_type']
        make = listing['metadata']['make']
        model = listing['metadata']['model']

        vehicle_types.add(vehicle_type)
        makes.add(make)
        models.add(model)

        if vehicle_type not in vehicle_type_to_makes:
            vehicle_type_to_makes[vehicle_type] = set()
        vehicle_type_to_makes[vehicle_type].add(make)

        # Update make -> models map
        if make not in make_to_models:
            make_to_models[make] = set()
        make_to_models[make].add(model)

    for vehicle_type in vehicle_type_to_makes:
        vehicle_type_to_makes[vehicle_type] = list(vehicle_type_to_makes[vehicle_type])

    for make in make_to_models:
        make_to_models[make] = list(make_to_models[make])

    years = ["Any Year", "1990", "1996", "1998", "2000", "2002", "2004", "2006", "2008", "2010", "2012", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"]
    kms = ["Any Kms", "30,000 kms", "60,000 kms", "100,000 kms", "150,000 kms", "200,000 kms"]
    prices = ["Any Price", "$2k", "$5k", "$8k", "$10k", "$12k", "$15k", "$20k", "$25k", "$30k"]

    return json.dumps({
        "vehicle_type_to_makes": vehicle_type_to_makes,
        "make_to_models": make_to_models,
        'vehicle_types': list(vehicle_types),
        'makes': list(makes),
        'models': list(models),
        "years": years,
        "kms": kms,
        "prices": prices,
    })


from tinydb import where


def structured_search(selected_vehicle_type: Optional[str], selected_make: Optional[str], selected_model: Optional[str], selected_year_from: Optional[str], selected_year_to: Optional[str], selected_kms_from: Optional[str], selected_kms_to: Optional[str], selected_price_from: Optional[str], selected_price_to: Optional[str]):
    # Start with a condition that should match everything
    conditions = [where('metadata').exists()]

    log.info('structured search')
    log.info(selected_vehicle_type)
    log.info(selected_make)
    log.info(selected_model)
    log.info(selected_year_from)
    log.info(selected_year_to)
    log.info(selected_kms_from)
    log.info(selected_kms_to)
    log.info(selected_price_from)
    log.info(selected_price_to)

    if selected_vehicle_type:
        log.info(f'selected_vehicle_type: {selected_vehicle_type}')
        conditions.append(where('metadata')['vehicle_type'] == selected_vehicle_type)

    if selected_make:
        log.info(f'selected_make: {selected_make}')
        conditions.append(where('metadata')['make'] == selected_make)

    if selected_model:
        log.info(f'selected_model: {selected_model}')
        conditions.append(where('metadata')['model'] == selected_model)

    if selected_year_from and selected_year_from != 'Any Year':
        log.info(f'selected_year_from: {selected_year_from}')
        conditions.append(where('metadata')['year'] >= int(selected_year_from))

    if selected_year_to and selected_year_to != 'Any Year':
        log.info(f'selected_year_to: {selected_year_to}')
        conditions.append(where('metadata')['year'] <= int(selected_year_to))

    if selected_kms_from and selected_kms_from != 'Any Kms':
        log.info(f'selected_kms_from: {selected_kms_from}')
        conditions.append(where('metadata')['kms'] >= int(selected_kms_from))

    if selected_kms_to and selected_kms_to != 'Any Kms':
        log.info(f'selected_kms_to: {selected_kms_to}')
        conditions.append(where('metadata')['kms'] <= int(selected_kms_to))

    if selected_price_from and selected_price_from != 'Any Price':
        log.info(f'selected_price_from: {selected_price_from}')
        conditions.append(where('metadata')['price'] >= float(selected_price_from))

    if selected_price_to and selected_price_to != 'Any Price':
        log.info(f'selected_price_to: {selected_price_to}')
        conditions.append(where('metadata')['price'] <= float(selected_price_to))

    # Combine all conditions with AND
    query = conditions[0]
    for condition in conditions[1:]:
        query = query & condition

    log.info(f'query: {query}')

    all_results = db.search(query)
    result = all_results[:7]

    prompt = PromptTemplate(
        template="""summarize the following search results so they can be displayed
        Vehicle Descriptions:
        {vehicle_descriptions}
        """,
        input_variables=["vehicle_descriptions"],
    )

    structured_llm = llm.with_structured_output(VehicleSearchResults)
    chain = prompt | structured_llm
    response: dict | VehicleSearchResults = chain.invoke({'vehicle_descriptions': result})
    log.info(f'response: {response}')
    return response.model_dump()

structured_search_options_tool = StructuredTool.from_function(
    func=structured_search_options,
    name="structured_search_options",
    description="""
        Useful for finding options available for structured search. Only use this tool when the user asks to do a structured search.
        """,
)

structured_search_tool = StructuredTool.from_function(
    func=structured_search,
    name="structured_search",
    description="""
    Useful for doing structured search. No arguments are required for this tool. as it able read them internally
    """,
    args_schema=StructuredSearchInput,
)

if __name__ == '__main__':
    print(structured_search_options())
    structured_search(StructuredSearchInput(
        selected_vehicle_type = 'SUV',
        selected_make = 'Ford',
        selected_model = 'Ranger Wildtrak X'
    ))