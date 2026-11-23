from __future__ import annotations

import unicodedata
from collections import Counter, defaultdict
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    METRIC_TYPES,
    Mineral,
    NationalProduction,
    Province,
    ProvincialMineralRecord,
)


def normalize_vi(text: str | None) -> str:
    """Normalize Vietnamese string to lowercase ASCII for accent-insensitive matching."""
    if not text:
        return ""
    replaced = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", replaced)
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return " ".join(stripped.lower().split())


def get_health_counts(db: Session) -> dict[str, Any]:
    dialect = db.get_bind().dialect.name
    return {
        "status": "ok",
        "db_dialect": dialect,
        "provinces": db.scalar(select(func.count()).select_from(Province)) or 0,
        "minerals": db.scalar(select(func.count()).select_from(Mineral)) or 0,
        "national_production": db.scalar(select(func.count()).select_from(NationalProduction)) or 0,
        "provincial_mineral_records": db.scalar(
            select(func.count()).select_from(ProvincialMineralRecord)
        )
        or 0,
    }


def get_filters_metadata(db: Session) -> dict[str, Any]:
    minerals = db.scalars(
        select(Mineral).order_by(Mineral.mineral_group, Mineral.name)
    ).all()
    provinces = db.scalars(select(Province).order_by(Province.name)).all()

    group_order = ["Năng lượng", "Kim loại", "Phi kim loại"]
    present_groups = list(dict.fromkeys(m.mineral_group for m in minerals))
    groups = [g for g in group_order if g in present_groups] + [
        g for g in present_groups if g not in group_order
    ]

    return {
        "mineral_groups": groups,
        "metric_types": list(METRIC_TYPES),
        "minerals": [
            {
                "id": m.id,
                "name": m.name,
                "mineral_group": m.mineral_group,
                "national_reserve": float(m.national_reserve)
                if m.national_reserve is not None
                else None,
                "reserve_unit": m.reserve_unit,
                "source_url": m.source_url,
            }
            for m in minerals
        ],
        "provinces": [
            {
                "id": p.id,
                "name": p.name,
                "province_type": p.province_type,
                "merged_from": p.merged_from,
                "lat": float(p.lat),
                "lng": float(p.lng),
            }
            for p in provinces
        ],
    }


def list_provinces_summary(
    db: Session,
    group: str | None = None,
    mineral_id: str | None = None,
    metric_type: str | None = None,
    q: str | None = None,
) -> dict[str, Any]:
    provinces = db.scalars(select(Province).order_by(Province.name)).all()
    records = db.scalars(
        select(ProvincialMineralRecord).options(joinedload(ProvincialMineralRecord.mineral))
    ).all()

    records_by_province: dict[str, list[ProvincialMineralRecord]] = defaultdict(list)
    for rec in records:
        records_by_province[rec.province_id].append(rec)

    norm_q = normalize_vi(q)
    has_mineral_filter = bool(group or mineral_id or metric_type)

    items: list[dict[str, Any]] = []
    total_matched_provinces = 0
    total_matched_records = 0

    for prov in provinces:
        prov_records = records_by_province.get(prov.id, [])

        # Filter records by group, mineral_id, metric_type
        filtered_records: list[ProvincialMineralRecord] = []
        for rec in prov_records:
            if group and rec.mineral.mineral_group != group:
                continue
            if mineral_id and rec.mineral_id != mineral_id:
                continue
            if metric_type and rec.metric_type != metric_type:
                continue
            filtered_records.append(rec)

        # Text search matches province metadata OR mineral/mine metadata
        province_text_match = False
        if norm_q:
            prov_haystack = normalize_vi(f"{prov.name} {prov.merged_from} {prov.province_type} {prov.id}")
            province_text_match = norm_q in prov_haystack

            if not province_text_match:
                filtered_records = [
                    rec
                    for rec in filtered_records
                    if norm_q
                    in normalize_vi(
                        f"{rec.mineral.name} {rec.mineral.mineral_group} {rec.key_mines} {rec.notes or ''}"
                    )
                ]

        if norm_q and has_mineral_filter:
            has_match = len(filtered_records) > 0
        elif norm_q:
            has_match = province_text_match or len(filtered_records) > 0
        elif has_mineral_filter:
            has_match = len(filtered_records) > 0
        else:
            has_match = len(filtered_records) > 0

        distinct_minerals: list[dict[str, str]] = []
        seen_mineral_ids: set[str] = set()
        group_counts: Counter[str] = Counter()
        quantified_highlights: list[dict[str, Any]] = []

        for rec in filtered_records:
            group_counts[rec.mineral.mineral_group] += 1
            if rec.mineral_id not in seen_mineral_ids:
                seen_mineral_ids.add(rec.mineral_id)
                distinct_minerals.append(
                    {
                        "id": rec.mineral.id,
                        "name": rec.mineral.name,
                        "mineral_group": rec.mineral.mineral_group,
                    }
                )
            if rec.value is not None:
                quantified_highlights.append(
                    {
                        "mineral_id": rec.mineral_id,
                        "mineral_name": rec.mineral.name,
                        "metric_type": rec.metric_type,
                        "value": float(rec.value),
                        "unit": rec.unit,
                        "period": rec.period,
                    }
                )

        dominant_group = group_counts.most_common(1)[0][0] if group_counts else None

        if has_match:
            total_matched_provinces += 1
            total_matched_records += len(filtered_records)

        items.append(
            {
                "id": prov.id,
                "name": prov.name,
                "province_type": prov.province_type,
                "merged_from": prov.merged_from,
                "lat": float(prov.lat),
                "lng": float(prov.lng),
                "has_match": has_match,
                "total_records": len(prov_records),
                "matched_record_count": len(filtered_records),
                "distinct_mineral_count": len(distinct_minerals),
                "minerals": distinct_minerals,
                "mineral_groups": list(group_counts.keys()),
                "dominant_group": dominant_group,
                "highlights": quantified_highlights,
            }
        )

    # Sort for sidebar display: matched & richer provinces first, then alphabetically
    items.sort(
        key=lambda x: (
            not x["has_match"],
            -x["distinct_mineral_count"],
            -x["matched_record_count"],
            normalize_vi(x["name"]),
        )
    )

    return {
        "total_provinces": len(provinces),
        "matched_provinces": total_matched_provinces,
        "matched_records": total_matched_records,
        "filters_active": bool(has_mineral_filter or norm_q),
        "provinces": items,
    }


def get_province_detail(db: Session, province_id: str) -> dict[str, Any] | None:
    province = db.scalar(
        select(Province)
        .where(Province.id == province_id)
        .options(
            joinedload(Province.mineral_records).joinedload(ProvincialMineralRecord.mineral)
        )
    )
    if province is None:
        return None

    mineral_ids = list({rec.mineral_id for rec in province.mineral_records})
    nat_prod_by_mineral: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if mineral_ids:
        nat_rows = db.scalars(
            select(NationalProduction)
            .where(NationalProduction.mineral_id.in_(mineral_ids))
            .order_by(NationalProduction.mineral_id, NationalProduction.year)
        ).all()
        for row in nat_rows:
            nat_prod_by_mineral[row.mineral_id].append(
                {
                    "year": row.year,
                    "value": float(row.value),
                    "unit": row.unit,
                    "source_url": row.source_url,
                }
            )

    records_out = [
        {
            "id": rec.id,
            "mineral_id": rec.mineral_id,
            "mineral_name": rec.mineral.name,
            "mineral_group": rec.mineral.mineral_group,
            "metric_type": rec.metric_type,
            "value": float(rec.value) if rec.value is not None else None,
            "unit": rec.unit,
            "period": rec.period,
            "key_mines": rec.key_mines,
            "notes": rec.notes,
            "source_url": rec.source_url,
            "national_reserve": float(rec.mineral.national_reserve)
            if rec.mineral.national_reserve is not None
            else None,
            "reserve_unit": rec.mineral.reserve_unit,
            "mineral_source_url": rec.mineral.source_url,
            "national_production": nat_prod_by_mineral.get(rec.mineral_id, []),
        }
        for rec in sorted(
            province.mineral_records,
            key=lambda r: (r.mineral.mineral_group, r.mineral.name, r.period),
        )
    ]

    return {
        "id": province.id,
        "name": province.name,
        "province_type": province.province_type,
        "merged_from": province.merged_from,
        "lat": float(province.lat),
        "lng": float(province.lng),
        "distinct_mineral_count": len(mineral_ids),
        "record_count": len(records_out),
        "records": records_out,
    }


def get_statistics(
    db: Session,
    group: str | None = None,
    mineral_id: str | None = None,
) -> dict[str, Any]:
    provinces = db.scalars(select(Province)).all()
    minerals = db.scalars(select(Mineral).order_by(Mineral.mineral_group, Mineral.name)).all()
    records = db.scalars(
        select(ProvincialMineralRecord)
        .options(
            joinedload(ProvincialMineralRecord.province),
            joinedload(ProvincialMineralRecord.mineral),
        )
    ).all()
    nat_prod = db.scalars(
        select(NationalProduction)
        .options(joinedload(NationalProduction.mineral))
        .order_by(NationalProduction.mineral_id, NationalProduction.year)
    ).all()

    filtered_records = [
        r
        for r in records
        if (not group or r.mineral.mineral_group == group)
        and (not mineral_id or r.mineral_id == mineral_id)
    ]

    # Province ranking (provinces with at least 1 matching record)
    prov_minerals: dict[str, set[str]] = defaultdict(set)
    prov_records_count: Counter[str] = Counter()
    prov_names: dict[str, str] = {p.id: p.name for p in provinces}

    for rec in filtered_records:
        prov_minerals[rec.province_id].add(rec.mineral_id)
        prov_records_count[rec.province_id] += 1

    province_ranking = [
        {
            "province_id": pid,
            "province_name": prov_names[pid],
            "distinct_minerals": len(prov_minerals[pid]),
            "record_count": prov_records_count[pid],
        }
        for pid in prov_records_count
    ]
    province_ranking.sort(
        key=lambda x: (-x["distinct_minerals"], -x["record_count"], normalize_vi(x["province_name"]))
    )

    # Mineral group breakdown (both distinct minerals catalog & active provincial records)
    group_catalog: Counter[str] = Counter(m.mineral_group for m in minerals)
    group_records: Counter[str] = Counter(r.mineral.mineral_group for r in filtered_records)
    group_provinces: dict[str, set[str]] = defaultdict(set)
    for rec in filtered_records:
        group_provinces[rec.mineral.mineral_group].add(rec.province_id)

    ordered_groups = ["Năng lượng", "Kim loại", "Phi kim loại"]
    for g in list(group_catalog.keys()):
        if g not in ordered_groups:
            ordered_groups.append(g)

    group_breakdown = [
        {
            "group": g,
            "mineral_catalog_count": group_catalog.get(g, 0),
            "record_count": group_records.get(g, 0),
            "province_count": len(group_provinces.get(g, set())),
        }
        for g in ordered_groups
    ]

    # National reserves (minerals with quantified national_reserve)
    reserves = [
        {
            "mineral_id": m.id,
            "mineral_name": m.name,
            "mineral_group": m.mineral_group,
            "national_reserve": float(m.national_reserve),
            "reserve_unit": m.reserve_unit,
            "source_url": m.source_url,
        }
        for m in minerals
        if m.national_reserve is not None
        and (not group or m.mineral_group == group)
        and (not mineral_id or m.id == mineral_id)
    ]
    reserves.sort(key=lambda x: -x["national_reserve"])

    # National production comparison (2010 vs 2021)
    prod_by_mineral: dict[str, dict[str, Any]] = {}
    years_set: set[int] = set()
    for row in nat_prod:
        if group and row.mineral.mineral_group != group:
            continue
        if mineral_id and row.mineral_id != mineral_id:
            continue
        years_set.add(row.year)
        entry = prod_by_mineral.setdefault(
            row.mineral_id,
            {
                "mineral_id": row.mineral_id,
                "mineral_name": row.mineral.name,
                "unit": row.unit,
                "series": {},
            },
        )
        entry["series"][str(row.year)] = float(row.value)

    metric_counts = Counter(r.metric_type for r in filtered_records)

    return {
        "kpis": {
            "total_provinces": len(provinces),
            "provinces_with_minerals": len(prov_records_count),
            "total_minerals": len(minerals),
            "total_records": len(filtered_records),
            "quantified_records": sum(1 for r in filtered_records if r.value is not None),
        },
        "province_ranking": province_ranking,
        "group_breakdown": group_breakdown,
        "metric_breakdown": [
            {"metric_type": mt, "count": metric_counts.get(mt, 0)} for mt in METRIC_TYPES
        ],
        "national_reserves": reserves,
        "national_production": {
            "years": sorted(years_set),
            "items": list(prod_by_mineral.values()),
        },
    }
