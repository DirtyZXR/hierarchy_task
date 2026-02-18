from typing import Optional, List

from sqlalchemy import Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Hierarchy(Base):
    __tablename__ = "hierarhy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    id_parent: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("hierarhy.id"),
        nullable=True
    )

    name: Mapped[str] = mapped_column(String)
    image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    state: Mapped[Optional[int]] = mapped_column(Integer)

    parent: Mapped[Optional["Hierarchy"]] = relationship(
        back_populates="children",
        remote_side=[id]
    )

    children: Mapped[List["Hierarchy"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (f"<Hierarchy("
                f"id={self.id}, name={self.name}, state={self.state})>")