from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PlantStatus = Literal["operational", "planned", "construction", "paused", "retired"]
DataQualityGrade = Literal["A", "B", "C", "D", "E"]
EmissionType = Literal[
    "total_scope1_co2e",
    "fossil_co2",
    "biogenic_co2",
    "process_co2",
    "combustion_co2",
    "ch4",
    "n2o",
]
CapacityParameter = Literal["nameplate_capacity", "actual_production", "estimated_production"]
EnergyParameter = Literal[
    "electricity_consumption",
    "grid_factor",
    "scope2_co2e",
    "fuel_energy",
    "steam_demand",
    "waste_heat_temperature",
    "flue_gas_temperature",
    "capture_heat_available",
]
CaptureStatusValue = Literal[
    "none",
    "study",
    "pilot",
    "planned",
    "under-construction",
    "operational",
    "cancelled",
]
CaptureType = Literal[
    "none",
    "post-combustion",
    "pre-combustion",
    "process-stream",
    "oxyfuel",
    "direct-separation",
    "biogenic-CO2",
    "hybrid",
]
CaptureTechnology = Literal[
    "none",
    "amine",
    "adsorption",
    "membrane",
    "cryogenic",
    "carbonate-looping",
    "oxyfuel",
    "unknown",
]


class Plant(BaseModel):
    plant_id: str
    name: str
    operator: str
    sector: str
    municipality: str
    county: str
    status: PlantStatus
    primary_product: str
    start_year: int | None = None
    website: str | None = None
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class Location(BaseModel):
    location_id: str
    plant_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str
    municipality: str
    county: str
    coordinate_precision: str
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class Emission(BaseModel):
    emission_id: str
    plant_id: str
    year: int
    emission_type: EmissionType
    value: float = Field(ge=0)
    unit: str
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class Product(BaseModel):
    product_id: str
    plant_id: str
    product: str
    capacity_parameter: CapacityParameter
    value: float = Field(ge=0)
    unit: str
    year: int
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class PointSource(BaseModel):
    point_source_id: str
    plant_id: str
    source_name: str
    stream_type: str
    estimated_co2_concentration_pct: float = Field(ge=0, le=100)
    annual_co2_tonnes: float = Field(ge=0)
    capture_priority: str
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class CaptureStatus(BaseModel):
    capture_status_id: str
    plant_id: str
    capture_status: CaptureStatusValue
    capture_type: CaptureType
    capture_technology: CaptureTechnology
    target_capture_tonnes_per_year: float = Field(ge=0)
    storage_or_use_pathway: str
    status_notes: str
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class Energy(BaseModel):
    energy_id: str
    plant_id: str
    energy_parameter: EnergyParameter
    value: float = Field(ge=0)
    unit: str
    year: int
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class Logistics(BaseModel):
    logistics_id: str
    plant_id: str
    nearest_port: str
    port_distance_km: float = Field(ge=0)
    rail_access: bool
    storage_hub_candidate: str
    transport_notes: str
    reference_id: str
    data_quality: DataQualityGrade
    method: str


class Reference(BaseModel):
    reference_id: str
    title: str
    organization: str
    year: int
    url: str
    access_date: str
    document_type: str
    license: str
    notes: str


class DataQuality(BaseModel):
    data_quality: DataQualityGrade
    definition: str


class PlantDetail(BaseModel):
    plant: Plant
    location: Location | None
    emissions: list[Emission]
    products: list[Product]
    point_sources: list[PointSource]
    capture_status: list[CaptureStatus]
    energy: list[Energy]
    logistics: list[Logistics]
    data_quality: list[DataQuality]
