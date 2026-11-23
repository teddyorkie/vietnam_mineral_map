# Vietnam Mineral Map (34 Post-2025 Provinces & Cities)

Interactive Python web application built with **FastAPI + Jinja2 + Leaflet.js + Chart.js**, backed by **SQLite** (auto-seeded from `khoang_san_viet_nam_tinh.sql`) with optional **MySQL 8.0+** support via SQLAlchemy 2.0.

## Features
- **Interactive 34-Province Choropleth Map**: Post-2025 Vietnam administrative boundaries (plus Hoàng Sa & Trường Sa labels) with hover tooltips, click-to-zoom, dynamic color legend, and clean-canvas / CartoDB basemap toggle.
- **Smart Search & Multi-Filter**: Filter by mineral group (`Năng lượng`, `Kim loại`, `Phi kim loại`), mineral type, metric type (`annual_production`, `design_capacity`, `licensed_capacity`, `distribution_only`), or search diacritic-insensitively by province name, legacy pre-merger province name (e.g. `Đắk Nông`, `Dak Nong`, `Bà Rịa - Vũng Tàu`), mineral, or key mine (`Núi Pháo`, `Đông Pao`).
- **Province Detail Sidebar**: Shows merger history (`merged_from`), province type, coordinates, quantified production/capacity metrics, key mines, notes, national reserves, national output trends, and source links.
- **Statistics Dashboard**: Interactive Chart.js visualizations (province diversity ranking, mineral group distribution, national reserves, and 2010 vs 2021 national production comparison).
- **Bilingual UI (VI / EN)**: Instant Vietnamese / English toggle persisted in `localStorage`.

## Quick Start (with `uv`)

```powershell
# 1. Install dependencies
uv sync

# 2. (Optional) Rebuild SQLite DB from khoang_san_viet_nam_tinh.sql
# Note: The FastAPI app also auto-creates and seeds data/khoang_san_vn.db on startup.
uv run python scripts/init_db.py --reset

# 3. Run the web application
uv run uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

## Optional: Using MySQL 8.0+ Instead of SQLite

1. Import `khoang_san_viet_nam_tinh.sql` into your MySQL server.
2. Install the optional MySQL driver extra:
   ```powershell
   uv sync --extra mysql
   ```
3. Copy `.env.example` to `.env` and set `DATABASE_URL`:
   ```env
   DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/khoang_san_vn?charset=utf8mb4
   ```

## Regenerating the 34-Province GeoJSON

The web-optimized GeoJSON is bundled at `app/static/data/vietnam_provinces_34.geojson`. To regenerate it from the source GIS dataset:

```powershell
uv run python scripts/build_geojson.py
```

## Running Tests

```powershell
uv run pytest -v
```
