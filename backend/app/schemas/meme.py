from datetime import datetime

from pydantic import BaseModel, ConfigDict

class MemeCreate(BaseModel):
    name: str
    media_type: str
    media_url: str
    description: str | None = None
    
    
class MemeOut(BaseModel):
    id: int
    name: str
    media_type: str
    media_url: str
    description: str | None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)