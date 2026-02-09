from pydantic import BaseModel
from datetime import datetime

# User profile schema for responses
class UserRead(BaseModel):
    id: int
    auth_user_id: int
    full_name: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }

# Optional: schema for creating/updating profile
class UserCreate(BaseModel):
    full_name: str | None = None
