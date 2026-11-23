from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import (
    Mineral,
    NationalProduction,
    Province,
    ProvincialMineralRecord,
)

INSERT_HEADER_RE = re.compile(
    r"INSERT\s+INTO\s+`?(?P<table>[a-zA-Z_][a-zA-Z0-9_]*)`?\s*\((?P<cols>[^)]+)\)\s*VALUES\s*(?P<body>.*)",
    re.IGNORECASE | re.DOTALL,
)


def _split_sql_statements(sql_text: str) -> list[str]:
    """Split SQL text into statements on semicolons outside single-quoted strings and comments."""
    statements: list[str] = []
    buf: list[str] = []
    in_quote = False
    in_line_comment = False
    i = 0
    n = len(sql_text)

    while i < n:
        ch = sql_text[i]
        nxt = sql_text[i + 1] if i + 1 < n else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                buf.append(ch)
            i += 1
            continue

        if not in_quote and ch == "-" and nxt == "-":
            in_line_comment = True
            i += 2
            continue

        if ch == "'":
            buf.append(ch)
            if in_quote:
                if nxt == "'":
                    buf.append(nxt)
                    i += 2
                    continue
                in_quote = False
            else:
                in_quote = True
            i += 1
            continue

        if in_quote and ch == "\\" and nxt:
            buf.append(ch)
            buf.append(nxt)
            i += 2
            continue

        if not in_quote and ch == ";":
            stmt = "".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf.clear()
            i += 1
            continue

        buf.append(ch)
        i += 1

    trailing = "".join(buf).strip()
    if trailing:
        statements.append(trailing)
    return statements


def _parse_value_token(raw: str) -> Any:
    token = raw.strip()
    if not token or token.upper() == "NULL":
        return None
    if token.startswith("'") and token.endswith("'"):
        inner = token[1:-1]
        inner = inner.replace("''", "'").replace("\\'", "'").replace("\\n", "\n")
        return inner
    if re.fullmatch(r"-?\d+", token):
        return int(token)
    if re.fullmatch(r"-?\d+\.\d+", token):
        return Decimal(token)
    return token


def _parse_values_tuples(body: str) -> list[list[Any]]:
    """Parse VALUES (...), (...), ... into a list of typed Python lists."""
    rows: list[list[Any]] = []
    current_row: list[Any] | None = None
    buf: list[str] = []
    in_quote = False
    i = 0
    n = len(body)

    while i < n:
        ch = body[i]
        nxt = body[i + 1] if i + 1 < n else ""

        if in_quote:
            buf.append(ch)
            if ch == "\\" and nxt:
                buf.append(nxt)
                i += 2
                continue
            if ch == "'":
                if nxt == "'":
                    buf.append(nxt)
                    i += 2
                    continue
                in_quote = False
            i += 1
            continue

        if ch == "'":
            in_quote = True
            buf.append(ch)
            i += 1
            continue

        if ch == "(" and current_row is None:
            current_row = []
            buf.clear()
            i += 1
            continue

        if current_row is not None:
            if ch == ",":
                current_row.append(_parse_value_token("".join(buf)))
                buf.clear()
                i += 1
                continue
            if ch == ")":
                current_row.append(_parse_value_token("".join(buf)))
                buf.clear()
                rows.append(current_row)
                current_row = None
                i += 1
                continue
            buf.append(ch)

        i += 1

    return rows


def parse_seed_sql(sql_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Extract INSERT INTO rows for each table from the MySQL seed dump."""
    sql_text = sql_path.read_text(encoding="utf-8")
    data: dict[str, list[dict[str, Any]]] = {
        "provinces": [],
        "minerals": [],
        "national_production": [],
        "provincial_mineral_records": [],
    }

    for stmt in _split_sql_statements(sql_text):
        match = INSERT_HEADER_RE.match(stmt)
        if not match:
            continue
        table = match.group("table").lower()
        if table not in data:
            continue
        cols = [c.strip().strip("`") for c in match.group("cols").split(",")]
        tuples = _parse_values_tuples(match.group("body"))
        for values in tuples:
            if len(values) != len(cols):
                raise ValueError(
                    f"Column count mismatch in table {table}: expected {len(cols)}, got {len(values)}"
                )
            data[table].append(dict(zip(cols, values)))

    return data


def seed_database(session: Session, sql_path: Path, reset: bool = False) -> dict[str, int]:
    """Seed all 4 mineral map tables from khoang_san_viet_nam_tinh.sql."""
    existing_provinces = session.scalar(select(func.count()).select_from(Province)) or 0
    if existing_provinces > 0 and not reset:
        return {
            "provinces": existing_provinces,
            "minerals": session.scalar(select(func.count()).select_from(Mineral)) or 0,
            "national_production": session.scalar(
                select(func.count()).select_from(NationalProduction)
            )
            or 0,
            "provincial_mineral_records": session.scalar(
                select(func.count()).select_from(ProvincialMineralRecord)
            )
            or 0,
        }

    parsed = parse_seed_sql(sql_path)

    if reset:
        session.execute(delete(ProvincialMineralRecord))
        session.execute(delete(NationalProduction))
        session.execute(delete(Mineral))
        session.execute(delete(Province))
        session.flush()

    session.add_all([Province(**row) for row in parsed["provinces"]])
    session.add_all([Mineral(**row) for row in parsed["minerals"]])
    session.flush()
    session.add_all([NationalProduction(**row) for row in parsed["national_production"]])
    session.add_all([ProvincialMineralRecord(**row) for row in parsed["provincial_mineral_records"]])
    session.commit()

    return {table: len(rows) for table, rows in parsed.items()}
