from typing import Optional

from sqlmodel import Field, SQLModel


class MarginConfig(SQLModel, table=True):
    __tablename__ = "margin_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    part_category: str   # e.g., "electrical_parts", "motor_parts", "industrial_supplies"
    margin_pct: float    # e.g., 25.0 for 25%


class TaxConfig(SQLModel, table=True):
    __tablename__ = "tax_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    tax_name: str        # e.g., "GST", "Sales Tax"
    rate_pct: float      # e.g., 17.0 for 17%
