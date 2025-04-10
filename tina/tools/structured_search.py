import json
import logging
from typing import Annotated

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
db = TinyDB('db/db.json')


class StructuredSearchOptionsInput(BaseModel):
    state: Annotated[dict, InjectedState] = Field(description="current state")


def structured_search_options(state: Annotated[dict, InjectedState]):
    selected_make = None
    selected_vehicle_type = None
    if 'structured_search' in state:
        selected_vehicle_type = state['structured_search']['selected_vehicle_type']
        selected_make = state['structured_search']['selected_make']

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

    return json.dumps({
        "models": models,
        "makes": makes,
        "vehicle_types": vehicle_types,
    })



structured_search_options_tool = StructuredTool.from_function(
    func=structured_search_options,
    name="structured_search_options",
    description="""
        Useful for finding options available for structured search.
        """,
    args_schema=StructuredSearchOptionsInput,
)

if __name__ == '__main__':
    structured_search_options()