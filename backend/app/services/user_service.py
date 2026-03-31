from fastapi import HTTPException
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


def list_users():
    with SessionLocal() as session:
        users = session.scalars(select(User)).all()
        return users


def find_user_by_id(user_id: int):
    with SessionLocal() as session:
        user = session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario não encontrado")

        return user


def find_user_by_username(username: str):
    with SessionLocal() as session:
        user = session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

        return user


def find_user_by_email(email: str):
    with SessionLocal() as session:
        user = session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        return user


def create_new_user(user_data: UserCreate):
    with SessionLocal() as session:
        existing_username = session.execute(
            select(User).where(User.username == user_data.username)
        ).scalar_one_or_none()

        if existing_username:
            raise HTTPException(status_code=400, detail="username ja existente")

        existing_email = session.execute(
            select(User).where(User.email == user_data.email)
        ).scalar_one_or_none()

        if existing_email:
            raise HTTPException(status_code=400, detail="email ja existente")

        hashed_password = get_password_hash(user_data.password)

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user