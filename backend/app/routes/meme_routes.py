from fastapi import APIRouter

from app.schemas.meme import MemeCreate, MemeOut
from app.services.meme_service import(
    create_meme,
    list_all_meme,
    list_active_memes,
    get_meme_by_id,
    get_meme_by_name
)

router = APIRouter()

@router.post("/memes", response_model=MemeOut, status_code=201)
def create_new_meme(meme_data: MemeCreate):
    return create_meme(meme_data)

@router.get("/memes", response_model=list[MemeOut])
def list_memes():
    return list_all_meme()

@router.get("/memes/active", response_model=list[MemeOut])
def list_only_active_memes():
    return list_active_memes()

@router.get("/memes/{meme_id}", response_model=MemeOut)
def get_meme(meme_id: int):
    return get_meme_by_id(meme_id)

@router.get("/memes/name/{name}", response_model=MemeOut)
def get_meme_name(name: str):
    return get_meme_by_name(name)