from pydantic import BaseModel

class RecognitionCreate(BaseModel):
    meme_name: str
    confidence: float
    
class RecognitionResponse(BaseModel):
    history_id: int
    meme_name: str
    confidence: float
    media_type: str
    media_url: str
    description: str |  None