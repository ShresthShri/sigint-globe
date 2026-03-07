from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AircraftObservation(Base):
    __tablename__ = "aircraft_observation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collection_snapshot.id"), index=True
    )

    hex: Mapped[str] = mapped_column(String(8), index=True)
    flight: Mapped[str | None] = mapped_column(String(16), nullable=True)
    reg: Mapped[str | None] = mapped_column(String(16), nullable=True)
    ac_type: Mapped[str | None] = mapped_column(String(8), nullable=True)

    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    alt_baro: Mapped[int | None] = mapped_column(Integer, nullable=True)

    nac_p: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    nic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sil: Mapped[int | None] = mapped_column(Integer, nullable=True)

    gs: Mapped[float | None] = mapped_column(Float, nullable=True)
    tas: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_military: Mapped[bool] = mapped_column(Boolean, default=False)
    squawk: Mapped[str | None] = mapped_column(String(8), nullable=True)

    snapshot = relationship("CollectionSnapshot", back_populates="observations")

    def __repr__(self) -> str:
        return (
            f"<Aircraft {self.hex} flight={self.flight} "
            f"nac_p={self.nac_p} lat={self.lat:.2f} lon={self.lon:.2f}>"
        )
