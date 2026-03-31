from fastapi import APIRouter, Depends

from app.models.user import User

from app.routes.auth_routes import get_current_user
from app.schemas.recognition import RecognitionCreate, RecognitionResponse
from app.services.recognition_service import process_recognition

router = APIRouter()


@router.post("/recognition", response_model=RecognitionResponse)
def recognize_meme(
    recognition_data: RecognitionCreate,
    current_user: User = Depends(get_current_user)
): 
    return process_recognition(current_user.id, recognition_data)
