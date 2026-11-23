from __future__ import annotations


def test_index_html_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Bản Đồ Khoáng Sản Việt Nam" in resp.text
    assert "__INITIAL_I18N__" in resp.text
    assert "leaflet" in resp.text.lower()


def test_health_endpoint_counts(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["db_dialect"] == "sqlite"
    assert body["provinces"] == 34
    assert body["minerals"] == 13
    assert body["national_production"] == 6
    assert body["provincial_mineral_records"] == 22


def test_filters_metadata(client):
    resp = client.get("/api/filters")
    assert resp.status_code == 200
    body = resp.json()
    assert body["mineral_groups"] == ["Năng lượng", "Kim loại", "Phi kim loại"]
    assert len(body["minerals"]) == 13
    assert len(body["provinces"]) == 34
    assert "annual_production" in body["metric_types"]


def test_provinces_unfiltered_returns_all_34(client):
    resp = client.get("/api/provinces")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_provinces"] == 34
    assert len(body["provinces"]) == 34
    assert body["matched_records"] == 22
    assert body["matched_provinces"] == 15


def test_provinces_filter_by_group_and_mineral(client):
    resp = client.get("/api/provinces", params={"group": "Năng lượng"})
    assert resp.status_code == 200
    body = resp.json()
    matched_ids = {p["id"] for p in body["provinces"] if p["has_match"]}
    assert matched_ids == {"22", "79"}

    resp_bauxite = client.get("/api/provinces", params={"mineral_id": "bo_xit"})
    assert resp_bauxite.status_code == 200
    bauxite_ids = {p["id"] for p in resp_bauxite.json()["provinces"] if p["has_match"]}
    assert bauxite_ids == {"68", "08", "04", "20", "64", "51"}


def test_provinces_filter_by_metric_type(client):
    resp = client.get("/api/provinces", params={"metric_type": "annual_production"})
    assert resp.status_code == 200
    matched_ids = {p["id"] for p in resp.json()["provinces"] if p["has_match"]}
    assert matched_ids == {"22"}


def test_provinces_search_legacy_merged_and_mines_diacritic_insensitive(client):
    # Legacy province name with Vietnamese diacritics
    r1 = client.get("/api/provinces", params={"q": "Đắk Nông"})
    assert r1.status_code == 200
    assert {p["id"] for p in r1.json()["provinces"] if p["has_match"]} == {"68"}

    # Same search without diacritics (ASCII)
    r2 = client.get("/api/provinces", params={"q": "Dak Nong"})
    assert r2.status_code == 200
    assert {p["id"] for p in r2.json()["provinces"] if p["has_match"]} == {"68"}

    # Key mine search ("Núi Pháo" -> Thái Nguyên 19)
    r3 = client.get("/api/provinces", params={"q": "Nui Phao"})
    assert r3.status_code == 200
    assert {p["id"] for p in r3.json()["provinces"] if p["has_match"]} == {"19"}


def test_province_detail_found_and_not_found(client):
    resp = client.get("/api/provinces/68")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Tỉnh Lâm Đồng"
    assert "Đắk Nông" in body["merged_from"]
    assert body["distinct_mineral_count"] == 2
    assert len(body["records"]) == 2
    mineral_ids = {r["mineral_id"] for r in body["records"]}
    assert mineral_ids == {"bo_xit", "ti_tan"}

    # Check Quang Ninh includes national production history for coal
    resp_qn = client.get("/api/provinces/22")
    assert resp_qn.status_code == 200
    qn_body = resp_qn.json()
    assert len(qn_body["records"]) == 2
    assert len(qn_body["records"][0]["national_production"]) == 2

    # Not found
    resp_404 = client.get("/api/provinces/999")
    assert resp_404.status_code == 404


def test_statistics_endpoint(client):
    resp = client.get("/api/statistics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["kpis"]["total_provinces"] == 34
    assert body["kpis"]["provinces_with_minerals"] == 15
    assert body["kpis"]["total_records"] == 22
    assert body["kpis"]["quantified_records"] == 4
    assert len(body["province_ranking"]) == 15
    assert len(body["national_reserves"]) == 9
    assert body["national_production"]["years"] == [2010, 2021]
    assert len(body["national_production"]["items"]) == 3
