from typing import Optional

from enum import Enum

from pydantic import BaseModel, Field


class FuelEnum(str, Enum):
    petrol = 'Petrol'
    diesel = 'Diesel'
    hybrid = 'Hybrid'


class LocationEnum(str, Enum):
    whangarei = "Whangarei", "Corner Walton Street and Maunu Road"
    westgate = "Westgate", "Corner of Fred Taylor Drive & Kakano Road"
    northShore = "North Shore", "201 Archers Road, Wairau Valley, Auckland"
    otahuhu = "Otahuhu", "1120 Great South Road, Otahuhu, Auckland"
    penrose = "Penrose", "1000 - 1008 Great South Road, Penrose"
    botany = "Botany", "183 Harris Road, East Tamaki"
    manukau = "Manukau", "590 Great South Road, Manukau, Auckland"
    te_rapa_road = "Te Rapa Road", "850 Te Rapa Road, Hamilton"
    avalon_drive = "Avalon Drive", "112 Avalon Drive, Hamilton"
    tauranga = "Tauranga", "26 Hull Road, Mt Maunganui, Tauranga"
    newPlymouth = "New Plymouth", "690 Devon Road, New Plymouth"
    napier = "Napier", "31 Pandora Road, Napier"
    rotorua = "Rotorua", "44 Fairy Springs Road, Fairy Springs, Rotorua"
    palmerstonNorth = "Palmerston North", "201 John F Kennedy Drive, Palmerston North"
    porirua = "Porirua", "9 John Seddon Drive, Elsdon, Porirua, Wellington"
    nelson = "Nelson", "85 St Vincent Street"
    christchurch = "Christchurch", "1 Detroit Place, Christchurch"
    timaru = "Timaru", "1 Meadows Road, Washdyke, Timaru"
    dunedin = "Dunedin", "112 Anzac Avenue, Dunedin"
    invercargill = "Invercargill", "26 North Road, Invercargill"
    auckland_trucks = "Turners Auckland Trucks", ""


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
