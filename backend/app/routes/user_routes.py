from fastapi import APIRouter

from app.schemas.user import UserOut, UserCreate
from app.services.user_service import (
    list_users,
    find_user_by_id,
    create_new_user
)

router = APIRouter()


@router.get("/users", response_model=list[UserOut])
def list_all_users():
    return list_users()


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int):
    return find_user_by_id(user_id)


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(user_data: UserCreate):
    return create_new_user(user_data)