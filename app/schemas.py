from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db_dialect: str
    provinces: int
    minerals: int
    national_production: int
    provincial_mineral_records: int


class MineralBrief(BaseModel):
    id: str
    name: str
    mineral_group: str


class MineralCatalogItem(MineralBrief):
    national_reserve: float | None = None
    reserve_unit: str | None = None
    source_url: str


class ProvinceBasic(BaseModel):
    id: str
    name: str
    province_type: str
    merged_from: str
    lat: float
    lng: float


class FilterMetadataResponse(BaseModel):
    mineral_groups: list[str]
    metric_types: list[str]
    minerals: list[MineralCatalogItem]
    provinces: list[ProvinceBasic]


class RecordHighlight(BaseModel):
    mineral_id: str
    mineral_name: str
    metric_type: str
    value: float
    unit: str | None = None
    period: str


class ProvinceMapItem(ProvinceBasic):
    has_match: bool
    total_records: int
    matched_record_count: int
    distinct_mineral_count: int
    minerals: list[MineralBrief]
    mineral_groups: list[str]
    dominant_group: str | None = None
    highlights: list[RecordHighlight]


class ProvincesSummaryResponse(BaseModel):
    total_provinces: int
    matched_provinces: int
    matched_records: int
    filters_active: bool
    provinces: list[ProvinceMapItem]


class NationalProductionPoint(BaseModel):
    year: int
    value: float
    unit: str
    source_url: str


class ProvincialMineralRecordOut(BaseModel):
    id: int
    mineral_id: str
    mineral_name: str
    mineral_group: str
    metric_type: str
    value: float | None = None
    unit: str | None = None
    period: str
    key_mines: str
    notes: str | None = None
    source_url: str
    national_reserve: float | None = None
    reserve_unit: str | None = None
    mineral_source_url: str
    national_production: list[NationalProductionPoint]


class ProvinceDetailResponse(ProvinceBasic):
    distinct_mineral_count: int
    record_count: int
    records: list[ProvincialMineralRecordOut]


class StatisticsKPIs(BaseModel):
    total_provinces: int
    provinces_with_minerals: int
    total_minerals: int
    total_records: int
    quantified_records: int


class ProvinceRankItem(BaseModel):
    province_id: str
    province_name: str
    distinct_minerals: int
    record_count: int


class GroupBreakdownItem(BaseModel):
    group: str
    mineral_catalog_count: int
    record_count: int
    province_count: int


class MetricBreakdownItem(BaseModel):
    metric_type: str
    count: int


class NationalReserveItem(BaseModel):
    mineral_id: str
    mineral_name: str
    mineral_group: str
    national_reserve: float
    reserve_unit: str | None = None
    source_url: str


class NationalProductionItem(BaseModel):
    mineral_id: str
    mineral_name: str
    unit: str
    series: dict[str, float]


class NationalProductionBlock(BaseModel):
    years: list[int]
    items: list[NationalProductionItem]


class StatisticsResponse(BaseModel):
    kpis: StatisticsKPIs
    province_ranking: list[ProvinceRankItem]
    group_breakdown: list[GroupBreakdownItem]
    metric_breakdown: list[MetricBreakdownItem]
    national_reserves: list[NationalReserveItem]
    national_production: NationalProductionBlock
