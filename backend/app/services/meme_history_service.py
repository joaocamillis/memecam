from fastapi import HTTPException
from sqlalchemy import select, desc

from app.core.database import SessionLocal
from app.models.meme_history import MemeHistory
from app.schemas.meme_history import MemeHistoryCreate


def create_meme_history(user_id: int, meme_data: MemeHistoryCreate):
    with SessionLocal() as session:
        new_history = MemeHistory(
            user_id = user_id,
            meme_name = meme_data.meme_name,
            confidence = meme_data.confidence,
            media_type = meme_data.media_type
        )
        
        session.add(new_history)
        session.commit()
        session.refresh(new_history)
        
        return new_history
    
    
def list_all_meme_history():
    with SessionLocal() as session:
        history = session.scalars(
            select(MemeHistory).order_by(desc(MemeHistory.created_at))
        ).all()
        
        return history
    
def list_meme_history_by_user(user_id: id):
    with SessionLocal() as session:
        history = session.scalars(
            select(MemeHistory)
            .where(MemeHistory.user_id == user_id)
            .order_by(desc(MemeHistory.created_at))
        ).all()
        
        return history
    
def get_meme_history_by_id(history_id: int):
    with SessionLocal() as session:
        history = session.execute(
            select(MemeHistory).where(MemeHistory.id == history_id)
        ).scalar_one_or_none()
        
        if history is None:
            raise HTTPException(status_code=404, detail="Historico nao encontrado")
        
        return history