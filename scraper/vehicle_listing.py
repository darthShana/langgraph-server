from typing import Optional

from enum import Enum

from pydantic import BaseModel, Field


class FuelEnum(str, Enum):
    petrol = 'Petrol'
    diesel = 'Diesel'
    hybrid = 'Hybrid'



class LocationEnum(str, Enum):
    whangarei = "Whangarei"
    westgate = "Westgate"
    northShore = "North Shore"
    otahuhu = "Otahuhu"
    penrose = "Penrose"
    botany = "Botany"
    manukau = "Manukau"
    te_rapa_road = "Te Rapa Road"
    avalon_drive = "Avalon Drive"
    tauranga = "Tauranga"
    newPlymouth = "New Plymouth"
    napier = "Napier"
    rotorua = "Rotorua"
    palmerstonNorth = "Palmerston North"
    porirua = "Porirua"
    nelson = "Nelson"
    christchurch = "Christchurch"
    timaru = "Timaru"
    dunedin = "Dunedin"
    invercargill = "Invercargill"
    auckland_trucks = "Turners Auckland Trucks"

# If you need to store the address as well, use a separate dictionary or class
LOCATION_ADDRESSES = {
    LocationEnum.whangarei: "Corner Walton Street and Maunu Road",
    LocationEnum.westgate: "Corner of Fred Taylor Drive & Kakano Road",
    LocationEnum.northShore: "201 Archers Road, Wairau Valley, Auckland",
    LocationEnum.otahuhu: "1120 Great South Road, Otahuhu, Auckland",
    LocationEnum.penrose: "1000 - 1008 Great South Road, Penrose",
    LocationEnum.botany: "183 Harris Road, East Tamaki",
    LocationEnum.manukau: "590 Great South Road, Manukau, Auckland",
    LocationEnum.te_rapa_road: "850 Te Rapa Road, Hamilton",
    LocationEnum.avalon_drive: "112 Avalon Drive, Hamilton",
    LocationEnum.tauranga: "26 Hull Road, Mt Maunganui, Tauranga",
    LocationEnum.newPlymouth: "690 Devon Road, New Plymouth",
    LocationEnum.napier: "31 Pandora Road, Napier",
    LocationEnum.rotorua: "44 Fairy Springs Road, Fairy Springs, Rotorua",
    LocationEnum.palmerstonNorth: "201 John F Kennedy Drive, Palmerston North",
    LocationEnum.porirua: "9 John Seddon Drive, Elsdon, Porirua, Wellington",
    LocationEnum.nelson: "85 St Vincent Street",
    LocationEnum.christchurch: "1 Detroit Place, Christchurch",
    LocationEnum.timaru: "1 Meadows Road, Washdyke, Timaru",
    LocationEnum.dunedin: "112 Anzac Avenue, Dunedin",
    LocationEnum.invercargill: "26 North Road, Invercargill",
    LocationEnum.auckland_trucks: "",
}


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
