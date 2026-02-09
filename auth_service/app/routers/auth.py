from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.core.config import settings 
router = APIRouter(prefix="/auth", tags=["Auth"])

bearer_scheme = HTTPBearer()


# ---------------- REGISTER ----------------
@router.post("/register")
async def register(email: str, password: str, db: Session = Depends(get_db)):
    print("Using database:", settings.DATABASE_URL)  #
    service = AuthService(db)
    user = service.register_user(email, password)
    return {"message": "User registered successfully", "user_id": user.id}


# ---------------- LOGIN ----------------
@router.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    service = AuthService(db)
    token = service.login_user(email, password)
    return {"access_token": token, "token_type": "bearer"}


# ---------------- VALIDATE TOKEN (MOST IMPORTANT) ----------------
@router.post("/validate-token")
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    service = AuthService(db)
    user_data = service.validate_token(token)

    return user_data
