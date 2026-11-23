from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import repository
from app.db.session import get_db
from app.schemas import (
    FilterMetadataResponse,
    HealthResponse,
    ProvinceDetailResponse,
    ProvincesSummaryResponse,
    StatisticsResponse,
)

router = APIRouter(prefix="/api", tags=["minerals"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/health", response_model=HealthResponse)
def health(db: DbSession):
    return repository.get_health_counts(db)


@router.get("/filters", response_model=FilterMetadataResponse)
def get_filters(db: DbSession):
    return repository.get_filters_metadata(db)


@router.get("/provinces", response_model=ProvincesSummaryResponse)
def list_provinces(
    db: DbSession,
    group: Annotated[
        str | None,
        Query(description="Mineral group (Năng lượng, Kim loại, Phi kim loại)"),
    ] = None,
    mineral_id: Annotated[
        str | None,
        Query(description="Mineral ID (e.g., bo_xit, than_da)"),
    ] = None,
    metric_type: Annotated[
        str | None,
        Query(description="Metric type enum"),
    ] = None,
    q: Annotated[
        str | None,
        Query(description="Search query (province, legacy merged name, mineral, mine)"),
    ] = None,
):
    return repository.list_provinces_summary(
        db=db,
        group=group or None,
        mineral_id=mineral_id or None,
        metric_type=metric_type or None,
        q=q or None,
    )


@router.get("/provinces/{province_id}", response_model=ProvinceDetailResponse)
def get_province(province_id: str, db: DbSession):
    detail = repository.get_province_detail(db=db, province_id=province_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Province '{province_id}' not found")
    return detail


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(
    db: DbSession,
    group: Annotated[str | None, Query()] = None,
    mineral_id: Annotated[str | None, Query()] = None,
):
    return repository.get_statistics(
        db=db,
        group=group or None,
        mineral_id=mineral_id or None,
    )


@router.get("/geojson")
def get_geojson():
    geo_path = settings.resolved_geojson_path
    if not geo_path.exists():
        raise HTTPException(
            status_code=503,
            detail="GeoJSON boundary file not found. Run `uv run python scripts/build_geojson.py`.",
        )
    return FileResponse(
        path=geo_path,
        media_type="application/geo+json",
        headers={"Cache-Control": "public, max-age=86400"},
    )
