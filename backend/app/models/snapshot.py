from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CollectionSnapshot(Base):
    __tablename__ = "collection_snapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    region_name: Mapped[str] = mapped_column(String(64), index=True)
    aircraft_total: Mapped[int] = mapped_column(Integer, default=0)
    aircraft_with_nacp: Mapped[int] = mapped_column(Integer, default=0)
    aircraft_low_nacp: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)

    observations = relationship(
        "AircraftObservation", back_populates="snapshot", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Snapshot {self.id} region={self.region_name} "
            f"aircraft={self.aircraft_total} low_nacp={self.aircraft_low_nacp}>"
        )
