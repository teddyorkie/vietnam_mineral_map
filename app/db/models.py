from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


METRIC_TYPES = (
    "annual_production",
    "design_capacity",
    "licensed_capacity",
    "distribution_only",
)


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    province_type: Mapped[str] = mapped_column(String(50), nullable=False)
    merged_from: Mapped[str] = mapped_column(String(150), nullable=False)
    lat: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    lng: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)

    mineral_records: Mapped[list[ProvincialMineralRecord]] = relationship(
        back_populates="province",
        cascade="all, delete-orphan",
    )


class Mineral(Base):
    __tablename__ = "minerals"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mineral_group: Mapped[str] = mapped_column(String(50), nullable=False)
    national_reserve: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    reserve_unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)

    provincial_records: Mapped[list[ProvincialMineralRecord]] = relationship(
        back_populates="mineral",
        cascade="all, delete-orphan",
    )
    national_productions: Mapped[list[NationalProduction]] = relationship(
        back_populates="mineral",
        cascade="all, delete-orphan",
    )


class NationalProduction(Base):
    __tablename__ = "national_production"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mineral_id: Mapped[str] = mapped_column(String(50), ForeignKey("minerals.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)

    mineral: Mapped[Mineral] = relationship(back_populates="national_productions")


class ProvincialMineralRecord(Base):
    __tablename__ = "provincial_mineral_records"
    __table_args__ = (
        CheckConstraint(
            "metric_type IN ('annual_production', 'design_capacity', 'licensed_capacity', 'distribution_only')",
            name="ck_provincial_mineral_records_metric_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    province_id: Mapped[str] = mapped_column(String(10), ForeignKey("provinces.id"), nullable=False)
    mineral_id: Mapped[str] = mapped_column(String(50), ForeignKey("minerals.id"), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[Decimal | None] = mapped_column(Numeric(16, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    period: Mapped[str] = mapped_column(String(30), nullable=False)
    key_mines: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)

    province: Mapped[Province] = relationship(back_populates="mineral_records")
    mineral: Mapped[Mineral] = relationship(back_populates="provincial_records")
