from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------- REGISTER ----------------
    def register_user(self, email: str, password: str) -> User:
        user = User(
            email=email,
            password_hash=hash_password(password),
            is_active=True
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    # ---------------- LOGIN ----------------
    def login_user(self, email: str, password: str) -> str:
        user = self.db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        token = create_access_token({"sub": str(user.id)})
        return token

    # ---------------- VALIDATE TOKEN (MOST IMPORTANT) ----------------
    def validate_token(self, token: str) -> dict:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user = self.db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return {
            "user_id": user.id,
            "email": user.email
        }
