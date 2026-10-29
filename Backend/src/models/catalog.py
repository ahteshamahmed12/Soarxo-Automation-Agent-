from typing import Optional

from sqlmodel import Field, SQLModel


class Catalog(SQLModel, table=True):
    __tablename__ = "catalogs"

    id: Optional[int] = Field(default=None, primary_key=True)
    part_category: str   # e.g., "electrical_parts", "motor_parts", "industrial_supplies"
    file_name: str       # e.g., "electrical_parts_catalog.pdf"
    file_path: str       # local path or URL
    whatsapp_url: Optional[str] = None  # shared link URL for WhatsApp
    keywords: str = ""   # comma-separated keywords for matching inquiries
    active: bool = True
