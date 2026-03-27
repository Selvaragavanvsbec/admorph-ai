from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.db import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product: Mapped[str] = mapped_column(String(255), nullable=False)
    audience: Mapped[str] = mapped_column(String(255), nullable=False)
    goal: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    variants: Mapped[list["AdVariant"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class AdVariant(Base):
    __tablename__ = "ad_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    cta: Mapped[str] = mapped_column(String(128), nullable=False)
    layout: Mapped[str] = mapped_column(String(64), nullable=False)
    visual_theme: Mapped[str] = mapped_column(String(128), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    image_path: Mapped[str] = mapped_column(Text, nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="variants")
