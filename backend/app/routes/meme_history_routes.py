from fastapi import APIRouter, Depends

from app.models.user import User
from app.routes.auth_routes import get_current_user
from app.schemas.meme_history import MemeHistoryCreate, MemeHistoryOut

from app.services.meme_history_service import(
    create_meme_history,
    list_all_meme_history,
    list_meme_history_by_user,
    get_meme_history_by_id
)

router = APIRouter()

@router.post("/memes/history", response_model=MemeHistoryOut, status_code=201)
def create_history( 
    meme_data:MemeHistoryCreate,
    current_user: User = Depends(get_current_user)
):
    return create_meme_history(current_user.id, meme_data)

@router.get("/memes/history", response_model=list[MemeHistoryOut])
def list_history():
    return list_all_meme_history()

@router.get("/memes/history/user/{user_id}", response_model=list[MemeHistoryOut])
def list_history_by_user(user_id: int):
    return list_meme_history_by_user(user_id)

@router.get("/memes/history/{history_id}")
def get_history_by_id(history_id:int):
    return get_meme_history_by_id(history_id)

@router.get("/me/memes/history/", response_model=list[MemeHistoryOut])
def list_my_history(current_user: User = Depends(get_current_user)):
    return list_meme_history_by_user(current_user.id)

