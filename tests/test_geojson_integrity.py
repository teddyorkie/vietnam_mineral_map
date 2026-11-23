from __future__ import annotations

import json

from app.config import PROJECT_ROOT, settings
from app.db.seed import parse_seed_sql


def test_geojson_matches_all_34_database_provinces(client):
    geo_path = settings.resolved_geojson_path
    assert geo_path.exists(), f"Missing GeoJSON at {geo_path}"
    assert geo_path.stat().st_size < 2 * 1024 * 1024, "GeoJSON should stay compact (< 2 MB)"

    geojson = json.loads(geo_path.read_text(encoding="utf-8"))
    assert geojson["type"] == "FeatureCollection"
    features = geojson["features"]
    assert len(features) == 34

    parsed_sql = parse_seed_sql(PROJECT_ROOT / "khoang_san_viet_nam_tinh.sql")
    expected_ids = {p["id"] for p in parsed_sql["provinces"]}
    geo_ids = [f["properties"]["province_id"] for f in features]

    assert len(geo_ids) == len(set(geo_ids)), "Duplicate province_id entries in GeoJSON"
    assert set(geo_ids) == expected_ids

    for feat in features:
        assert feat["geometry"]["type"] in ("Polygon", "MultiPolygon")
        assert len(feat["geometry"]["coordinates"]) > 0

    # Also verify endpoint serves it cleanly
    resp = client.get("/api/geojson")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/geo+json")
