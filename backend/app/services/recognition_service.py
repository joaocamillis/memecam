from fastapi import HTTPException
from sqlalchemy import select

from app.schemas.recognition import RecognitionCreate,RecognitionResponse
from app.core.database import SessionLocal
from app.models.meme import Meme
from app.models.meme_history import MemeHistory

def process_recognition(user_id: int, recognition_data: RecognitionCreate):
    with SessionLocal() as session:
        meme = session.execute(
            select(Meme).where(Meme.name == recognition_data.meme_name)
        ).scalar_one_or_none()
        
        if not meme:
            raise HTTPException(status_code=404, detail="meme não encontrado no catalogo")
        
        if  not Meme.is_active:
            raise HTTPException(status_code=400, detail="Meme inativo")
        
        new_history = MemeHistory(
            user_id = user_id,
            meme_name = meme.name,
            confidence = recognition_data.confidence,
            media_type = meme.media_type
        )
        
        session.add(new_history)
        session.commit()
        session.refresh(new_history)
        
        return {
            "history_id": new_history.id,
            "meme_name": meme.name,
            "confidence": recognition_data.confidence,
            "media_type": meme.media_type,
            "media_url": meme.media_url,
            "description": meme.description
        }