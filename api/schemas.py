from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PlantStatus = Literal["operational", "planned", "construction", "paused", "retired"]
CaptureReadiness = Literal["none", "screening", "pilot", "planned", "installed"]
QualityRating = Literal["high", "medium", "low"]


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


class Location(BaseModel):
    location_id: str
    plant_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str
    municipality: str
    county: str
    coordinate_precision: str


class Emission(BaseModel):
    emission_id: str
    plant_id: str
    year: int
    scope: str
    co2e_tonnes: float = Field(ge=0)
    source_id: str


class Product(BaseModel):
    product_id: str
    plant_id: str
    product: str
    annual_capacity_tonnes: float = Field(ge=0)
    capacity_year: int
    source_id: str


class PointSource(BaseModel):
    point_source_id: str
    plant_id: str
    source_name: str
    stream_type: str
    estimated_co2_concentration_pct: float = Field(ge=0, le=100)
    annual_co2_tonnes: float = Field(ge=0)
    capture_priority: str


class CaptureStatus(BaseModel):
    capture_status_id: str
    plant_id: str
    readiness: CaptureReadiness
    capture_technology: str
    target_capture_tonnes_per_year: float = Field(ge=0)
    storage_or_use_pathway: str
    status_notes: str


class Energy(BaseModel):
    energy_id: str
    plant_id: str
    electricity_demand_gwh: float = Field(ge=0)
    heat_demand_gwh: float = Field(ge=0)
    primary_energy_source: str
    grid_region: str
    source_id: str


class Logistics(BaseModel):
    logistics_id: str
    plant_id: str
    nearest_port: str
    port_distance_km: float = Field(ge=0)
    rail_access: bool
    storage_hub_candidate: str
    transport_notes: str


class Reference(BaseModel):
    source_id: str
    title: str
    publisher: str
    url: str
    accessed_date: str
    notes: str


class DataQuality(BaseModel):
    quality_id: str
    plant_id: str
    field_group: str
    rating: QualityRating
    rationale: str
    reviewed_date: str


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

