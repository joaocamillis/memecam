from datetime import datetime

from pydantic  import BaseModel, ConfigDict

class MemeHistoryCreate(BaseModel):
    meme_name:str
    confidence: float
    media_type: str
    
class MemeHistoryOut(BaseModel):
    id: int
    user_id: int
    meme_name: str
    confidence: float
    media_type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)