from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InterferenceCell(Base):
    __tablename__ = "interference_cell"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collection_snapshot.id"), index=True
    )

    h3_index: Mapped[str] = mapped_column(String(16), index=True)
    h3_resolution: Mapped[int] = mapped_column(Integer, default=4)

    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)

    aircraft_count: Mapped[int] = mapped_column(Integer)
    low_nac_count: Mapped[int] = mapped_column(Integer)
    interference_ratio: Mapped[float] = mapped_column(Float)
    avg_nac_p: Mapped[float] = mapped_column(Float)

    severity: Mapped[float] = mapped_column(Float, index=True)

    snapshot = relationship("CollectionSnapshot")

    def __repr__(self) -> str:
        return (
            f"<Cell {self.h3_index} severity={self.severity:.1f} "
            f"aircraft={self.aircraft_count} ratio={self.interference_ratio:.2f}>"
        )
