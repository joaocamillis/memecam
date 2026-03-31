from fastapi import HTTPException
from sqlalchemy import select, or_

from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token
from app.models.user import User


def authenticate_user(login: str, password: str):
    with SessionLocal() as session:
        user = session.execute(
            select(User).where(
                or_(
                    User.username == login,
                    User.email == login
                )
            )
        ).scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=400, detail="usuario não encontrado")

        password_is_correct = verify_password(
            password,
            user.password_hash
        )

        if not password_is_correct:
            raise HTTPException(status_code=401, detail="Senha incorreta")

        return user


def login_user(login: str, password: str):
    user = authenticate_user(login, password)

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_authenticated_user_by_token(user_id: int):
    with SessionLocal() as session:
        user = session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Não foi possível validar as credenciais",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user