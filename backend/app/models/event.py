"""
Each event has a headline, source, optional URL, and optional lat/long. 
The region_name links it to the monitored region so can show events alongside the interference data 
keywords_matched stores which keywords triggered the match such as GPS Jamming for debugging 
"""

from datetime import datetime, timezone 

from sqlalchemy import DateTime, Float, Integer, String, Text 
from sqlalchemy.orm import Mapped, mapped_column 

from app.database import Base 

class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) 
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    source: Mapped[str] = mapped_column(String(64))
    headline: Mapped[str] = mapped_column(String(512))
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    region_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    keywords_matched: Mapped[str | None] = mapped_column(String(256), nullable=True)

    def __repr__(self) -> str:
        return f"<Event {self.id} [{self.source}] {self.headline[:50]}>"
