from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class MemeHistory(Base):
    __tablename__ = "meme_history"
    
    id:Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    meme_name:Mapped[str] = mapped_column(String(100), nullable=False)
    confidence:Mapped[float] = mapped_column(Float, nullable=False)
    media_type:Mapped[str] = mapped_column(String(30), nullable=False)
    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    user = relationship("User")