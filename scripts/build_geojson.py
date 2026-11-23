"""Download, simplify, and normalize Vietnam's 34 post-2025 province boundaries to GeoJSON.

Matches every feature by normalized Vietnamese province name against
khoang_san_viet_nam_tinh.sql so every polygon receives the exact `province_id`
primary key used in the database (`01`..`96`).
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from shapely.geometry import mapping, shape

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.repository import normalize_vi
from app.db.seed import parse_seed_sql

SEED_SQL = PROJECT_ROOT / "khoang_san_viet_nam_tinh.sql"
OUTPUT_GEOJSON = PROJECT_ROOT / "app" / "static" / "data" / "vietnam_provinces_34.geojson"

FREE_GIS_URL = (
    "https://raw.githubusercontent.com/nguyenduy1133/Free-GIS-Data/main/"
    + urllib.parse.quote(
        "Vietnam Administrative Divisions (Post-2025) - Đơn vị hành chính Việt Nam (Từ 2025)"
    )
    + "/Provinces.geojson"
)

ENGLISH_NAMES: dict[str, str] = {
    "01": "Hanoi City",
    "04": "Cao Bang Province",
    "08": "Tuyen Quang Province",
    "10": "Lao Cai Province",
    "11": "Dien Bien Province",
    "12": "Lai Chau Province",
    "14": "Son La Province",
    "19": "Thai Nguyen Province",
    "20": "Lang Son Province",
    "22": "Quang Ninh Province",
    "25": "Phu Tho Province",
    "27": "Bac Ninh Province",
    "31": "Hai Phong City",
    "33": "Hung Yen Province",
    "37": "Ninh Binh Province",
    "38": "Thanh Hoa Province",
    "40": "Nghe An Province",
    "42": "Ha Tinh Province",
    "45": "Quang Tri Province",
    "46": "Hue City",
    "48": "Da Nang City",
    "51": "Quang Ngai Province",
    "56": "Khanh Hoa Province",
    "64": "Gia Lai Province",
    "66": "Dak Lak Province",
    "68": "Lam Dong Province",
    "72": "Tay Ninh Province",
    "75": "Dong Nai Province",
    "79": "Ho Chi Minh City",
    "86": "Vinh Long Province",
    "87": "Dong Thap Province",
    "89": "An Giang Province",
    "92": "Can Tho City",
    "96": "Ca Mau Province",
}


def strip_admin_prefix(name: str) -> str:
    norm = normalize_vi(name)
    for prefix in (
        "thanh pho ",
        "tp. ",
        "tp ",
        "tinh ",
        "thua thien ",
    ):
        if norm.startswith(prefix):
            norm = norm[len(prefix) :].strip()
    aliases = {
        "hcm": "ho chi minh",
        "tphcm": "ho chi minh",
        "ho chi minh city": "ho chi minh",
        "ha noi": "ha noi",
        "hanoi": "ha noi",
        "thua thien hue": "hue",
        "tp hue": "hue",
    }
    return aliases.get(norm, norm)


def round_coords(obj: Any, decimals: int = 4) -> Any:
    if isinstance(obj, (list, tuple)):
        if obj and isinstance(obj[0], (int, float)):
            return [round(float(v), decimals) for v in obj]
        return [round_coords(item, decimals) for item in obj]
    return obj


def extract_feature_name(props: dict[str, Any]) -> str:
    for key in (
        "TinhThanh",
        "ten_tinh",
        "Ten_Tinh",
        "TEN_TINH",
        "Name",
        "name",
        "NAME_1",
        "province_name",
        "ten",
        "Ten",
        "ADM1_VI",
        "VARNAME_1",
    ):
        val = props.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    # Fallback: pick first non-numeric string value
    for val in props.values():
        if isinstance(val, str) and len(val.strip()) > 2 and not val.strip().isdigit():
            return val.strip()
    return ""


def download_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "vietnam-mineral-map-builder/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _deg_dist_sq(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    return (lat1 - lat2) ** 2 + (lng1 - lng2) ** 2


def build_geojson(tolerance: float = 0.005) -> Path:
    parsed = parse_seed_sql(SEED_SQL)
    provinces = parsed["provinces"]
    by_core_name = {strip_admin_prefix(p["name"]): p for p in provinces}

    print(f"Downloading 34-province GeoJSON from:\n  {FREE_GIS_URL}")
    raw = download_json(FREE_GIS_URL)
    raw_features = raw.get("features", [])
    print(f"Downloaded {len(raw_features)} features.")

    matched_features: dict[str, list[Any]] = {}
    deferred_geoms: list[tuple[str, Any]] = []

    for feat in raw_features:
        props = feat.get("properties") or {}
        raw_name = extract_feature_name(props)
        core = strip_admin_prefix(raw_name)
        geom = shape(feat["geometry"])
        if not geom.is_valid:
            geom = geom.buffer(0)
        centroid = geom.centroid

        prov = by_core_name.get(core)
        if not prov:
            for candidate_key, candidate_prov in by_core_name.items():
                if candidate_key and (candidate_key in core or core in candidate_key):
                    prov = candidate_prov
                    break

        # Guard against upstream attribute typos (e.g. Dong Thap polygon mislabeled as Lang Son)
        if prov is not None:
            dist_sq = _deg_dist_sq(centroid.y, centroid.x, float(prov["lat"]), float(prov["lng"]))
            if dist_sq > 9.0:  # > 3 degrees (~330 km) off from expected centroid
                print(
                    f"  [!] Geometry labeled {raw_name!r} has centroid "
                    f"({centroid.y:.2f}N, {centroid.x:.2f}E), far from {prov['name']} "
                    f"({float(prov['lat']):.2f}N, {float(prov['lng']):.2f}E) — resolving by coordinates."
                )
                deferred_geoms.append((raw_name, geom))
                continue

        if prov is None:
            deferred_geoms.append((raw_name, geom))
            continue

        matched_features.setdefault(prov["id"], []).append(geom)

    # Resolve any deferred/mislabeled geometries by nearest unmatched province centroid
    unmatched_provs = [p for p in provinces if p["id"] not in matched_features]
    for raw_name, geom in deferred_geoms:
        centroid = geom.centroid
        if not unmatched_provs:
            continue
        nearest = min(
            unmatched_provs,
            key=lambda p: _deg_dist_sq(centroid.y, centroid.x, float(p["lat"]), float(p["lng"])),
        )
        dist = _deg_dist_sq(centroid.y, centroid.x, float(nearest["lat"]), float(nearest["lng"])) ** 0.5
        if dist < 2.0:
            print(
                f"  [+] Resolved deferred geometry ({raw_name!r}, centroid {centroid.y:.2f}N, {centroid.x:.2f}E) "
                f"-> {nearest['id']} {nearest['name']} (delta={dist:.2f}°)"
            )
            matched_features.setdefault(nearest["id"], []).append(geom)
            unmatched_provs.remove(nearest)

    missing = [p for p in provinces if p["id"] not in matched_features]
    if missing:
        raise RuntimeError(
            "Missing province boundaries for: "
            + ", ".join(f"{p['id']}:{p['name']}" for p in missing)
        )

    from shapely.ops import unary_union

    out_features: list[dict[str, Any]] = []
    for prov in sorted(provinces, key=lambda p: p["id"]):
        geoms = matched_features[prov["id"]]
        merged_geom = geoms[0] if len(geoms) == 1 else unary_union(geoms)
        simplified = merged_geom.simplify(tolerance, preserve_topology=True)
        if simplified.is_empty:
            simplified = merged_geom

        geom_dict = mapping(simplified)
        geom_dict["coordinates"] = round_coords(geom_dict["coordinates"], decimals=4)

        out_features.append(
            {
                "type": "Feature",
                "properties": {
                    "province_id": prov["id"],
                    "name_vi": prov["name"],
                    "name_en": ENGLISH_NAMES.get(prov["id"], prov["name"]),
                    "province_type": prov["province_type"],
                    "merged_from": prov["merged_from"],
                },
                "geometry": geom_dict,
            }
        )

    out_geojson = {
        "type": "FeatureCollection",
        "name": "vietnam_provinces_34_post_2025",
        "features": out_features,
    }

    OUTPUT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_GEOJSON.write_text(
        json.dumps(out_geojson, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    size_kb = OUTPUT_GEOJSON.stat().st_size / 1024
    print(f"Wrote {len(out_features)} province polygons to {OUTPUT_GEOJSON} ({size_kb:.1f} KB)")
    return OUTPUT_GEOJSON


if __name__ == "__main__":
    build_geojson()
