from fastapi import HTTPException
from sqlalchemy import select

from app.core.database import SessionLocal

from app.models.meme import Meme
from app.schemas.meme import MemeCreate

def create_meme(meme_data: MemeCreate):
    with SessionLocal() as session:
        existing_meme = session.execute(
            select(Meme).where(Meme.name == meme_data.name)
        ).scalar_one_or_none()
        
        if existing_meme:
            raise HTTPException(status_code=400, detail="meme ja existente")
        
        new_meme = Meme(
            name=meme_data.name,
            media_type=meme_data.media_type,
            media_url=meme_data.media_url,
            description=meme_data.description
        )
        
        session.add(new_meme)
        session.commit()
        session.refresh(new_meme)
        
        return new_meme
def list_all_meme():
    with SessionLocal() as session:
        memes = session.scalars(select(Meme)).all()
        return memes
    
def list_active_memes():
    with SessionLocal() as session:
        memes = session.scalars(
            select(Meme).where(Meme.is_active == True)
        ).all()
        
        return memes
    
def get_meme_by_id(meme_id: int):
    with SessionLocal() as session:
        meme = session.execute(
            select(Meme).where(Meme.id == meme_id)
        ).scalar_one_or_none()
        
        if meme is None:
            raise HTTPException(status_code=404, detail="meme nao encontrado")
        
        return meme
    
def get_meme_by_name(name: str):
    with SessionLocal() as session:
        memes = session.execute(
            select(Meme).where(Meme.name == name)
        ).scalar_one_or_none()
        
        if not memes:
            raise HTTPException(status_code=404, detail="meme não encontrado")

        return memes