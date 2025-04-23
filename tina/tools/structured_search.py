import json
import logging
from typing import Annotated

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


class StructuredSearchOptionsInput(BaseModel):
    state: Annotated[dict, InjectedState] = Field(description="current state")


def structured_search_options(state: Annotated[dict, InjectedState]):
    selected_make = None
    selected_vehicle_type = None
    if 'structured_search' in state:
        log.info(f'structured_search: {state["structured_search"]}')
        selected_vehicle_type = state['structured_search'].get('selected_vehicle_type', None)
        selected_make = state['structured_search'].get('selected_make', None)
    log.info(f'Selected vehicle type: {selected_vehicle_type}, Selected make: {selected_make}')

    Listing = Query()

    if selected_make and selected_vehicle_type:
        listings = db.search((Listing.metadata.vehicle_type == selected_vehicle_type) & (Listing.metadata.make == selected_make))
    elif selected_make:
        listings = db.search((Listing.metadata.make == selected_make))
    else:
        listings = db.search((Listing.metadata.exists()))

    models = map(lambda obj: obj['metadata']['model'], listings)
    models = list(set(filter(None, models)))
    log.info("models")
    log.info(models)

    if selected_vehicle_type:
        listings = db.search((Listing.metadata.vehicle_type == selected_vehicle_type))
    else:
        listings = db.search((Listing.metadata.exists()))

    makes = map(lambda obj: obj['metadata']['make'], listings)
    makes = list(set(filter(None, makes)))
    log.info("makes")
    log.info(makes)

    vehicle_types = map(lambda obj: obj['metadata']['vehicle_type'], listings)
    vehicle_types = list(set(filter(None, vehicle_types)))
    log.info("vehicle_types")
    log.info(vehicle_types)

    years = ["Any Year", "1990", "1996", "1998", "2000", "2002", "2004", "2006", "2008", "2010", "2012", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"]
    kms = ["Any Kms", "30,000 kms", "60,000 kms", "100,000 kms", "150,000 kms", "200,000 kms"]

    return json.dumps({
        "models": models,
        "makes": makes,
        "vehicle_types": vehicle_types,
        "years": years,
        "kms": kms
    })


from tinydb import where


def structured_search(state: Annotated[dict, InjectedState]):
    # Start with a condition that should match everything
    conditions = [where('metadata').exists()]

    if 'structured_search' in state:
        log.info(f'structured_search: {state["structured_search"]}')
    else:
        log.info('no structured search in state')

    if 'selected_vehicle_type' in state['structured_search'] and state['structured_search']['selected_vehicle_type']:
        log.info(f'selected_vehicle_type: {state["structured_search"]["selected_vehicle_type"]}')
        conditions.append(where('metadata')['vehicle_type'] == state['structured_search']['selected_vehicle_type'])

    if 'selected_make' in state['structured_search'] and state['structured_search']['selected_make']:
        log.info(f'selected_make: {state["structured_search"]["selected_make"]}')
        conditions.append(where('metadata')['make'] == state['structured_search']['selected_make'])

    if 'selected_model' in state['structured_search'] and state['structured_search']['selected_model']:
        log.info(f'selected_model: {state["structured_search"]["selected_model"]}')
        conditions.append(where('metadata')['model'] == state['structured_search']['selected_model'])

    if 'selected_year_from' in state['structured_search'] and state['structured_search']['selected_year_from']:
        log.info(f'selected_year_from: {state["structured_search"]["selected_year_from"]}')
        conditions.append(where('metadata')['year'] >= state['structured_search']['selected_year_from'])

    if 'selected_year_to' in state['structured_search'] and state['structured_search']['selected_year_to']:
        log.info(f'selected_year_to: {state["structured_search"]["selected_year_to"]}')
        conditions.append(where('metadata')['year'] <= state['structured_search']['selected_year_to'])

    if 'selected_kms_from' in state['structured_search'] and state['structured_search']['selected_kms_from']:
        log.info(f'selected_kms_from: {state["structured_search"]["selected_kms_from"]}')
        conditions.append(where('metadata')['kms'] >= state['structured_search']['selected_kms_from'])

    if 'selected_kms_to' in state['structured_search'] and state['structured_search']['selected_kms_to']:
        log.info(f'selected_kms_to: {state["structured_search"]["selected_kms_to"]}')
        conditions.append(where('metadata')['kms'] <= state['structured_search']['selected_kms_to'])

    # Combine all conditions with AND
    query = conditions[0]
    for condition in conditions[1:]:
        query = query & condition

    log.info(f'query: {query}')

    all_results = db.search(query)
    result = all_results[:7]
    log.info("result")
    log.info(result)

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
        Useful for finding options available for structured search. Always rerun this tool to get the options available, as they may change, DO NOT cache the results
        """,
    args_schema=StructuredSearchOptionsInput,
)

structured_search_tool = StructuredTool.from_function(
    func=structured_search,
    name="structured_search",
    description="""
    Useful for doing structured search. No arguments are required for this tool. as it able read them internally
    """,
    args_schema=StructuredSearchOptionsInput,
)

if __name__ == '__main__':
    structured_search({
        'structured_search': {
            # 'selected_vehicle_type': 'SUV',
            'selected_make': 'Ford',
            'selected_model': 'Ranger Wildtrak X'
        }
    })