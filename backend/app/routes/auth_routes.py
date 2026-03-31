import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserLogin, Token
from app.schemas.user import UserOut
from app.services.auth_service import (
    login_user,
    get_authenticated_user_by_token
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    return get_authenticated_user_by_token(int(user_id))


@router.post("/login", response_model=Token)
def login(user_data: UserLogin):
    return login_user(user_data.login, user_data.password)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user