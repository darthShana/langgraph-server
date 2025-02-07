from typing import Optional

from langchain_core.pydantic_v1 import BaseModel, Field
from enum import Enum


class FuelEnum(str, Enum):
    petrol = 'Petrol'
    diesel = 'Diesel'
    hybrid = 'Hybrid'


class LocationEnum(str, Enum):
    whangarei = "Whangarei",
    westgate = "Westgate",
    northShore = "North Shore",
    otahuhu = "Otahuhu",
    penrose = "Penrose",
    botany = "Botany",
    manukau = "Manukau",
    hamilton = "Hamilton"
    tauranga = "Tauranga",
    newPlymouth = "New Plymouth"
    napier = "Napier"
    rotorua = "Rotorua"
    palmerstonNorth = "Palmerston North"
    wellingto = "Wellington"
    porirua = "Porirua"
    nelson = "Nelson"
    christchurch = "Christchurch"
    timaru = "Timaru"
    dunedin = "Dunedin"
    invercargill = "Invercargill"
    auckland_trucks = "Turners Auckland Trucks"


class VehicleTypeEnum(str, Enum):
    wagon = 'Wagon',
    sedan = 'Sedan',
    hatchback = 'Hatchback',
    suv = 'SUV',
    utility = 'Utility',
    convertible = 'Convertible',
    sportsCar = 'Sports Car',
    van = 'Van',
    tractor = 'Tractor',
    excavator = 'Excavator',
    generator = 'Generator',
    fel ='FEL',
    roller = 'Roller'


class VehicleListingMetadata(BaseModel):
    make: str = Field("the manufacture of the vehicle listed")
    model: str = Field("the model of the vehicle listed")
    year: int = Field("the this vehicle was manufactures")
    fuel: FuelEnum = Field("the fuel type this vehicle uses")
    seats: Optional[int] = Field("the number of seats this vehicle has")
    odometer: Optional[int] = Field("odometer reading showing the vehicle milage")
    price: Optional[float] = Field("the price this vehicle is on sale for or the starting bid")
    location: Optional[LocationEnum] = Field("the location this vehicle is at")
    vehicle_type: VehicleTypeEnum = Field("the type for vehicle this is. eg car, van or SUV")
    colour: Optional[str] = Field("the colour of this vehicle")
    drive: Optional[str] = Field("describes the wheels that drive the vehicle")
    image: Optional[str] = Field("a image of this vehicle")


class VehicleListing(BaseModel):
    manufacturer_details: str = Field(description="details about the make, model, variant year model code etc")
    feature_details: str = Field(description="details about the features of the vehicle or its capabilities")
    condition_details: str = Field(description="details about the condition of the vehicle")
    possible_uses: str = Field(description="possible things this vehicle can be used for that may be different "
                                           "from other vehicle")
    other: str = Field(description="any details that doesnt fit in the other sections")
    metadata: VehicleListingMetadata = Field(description="metadata about the listing")
