from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from core.config import settings
from core.database import get_db
from services.user_service import UserService
from schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()


# ---------------- TOKEN VALIDATION ----------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.AUTH_SERVICE_URL}/auth/validate-token",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    data = resp.json()

    # Normalize contract (VERY IMPORTANT in microservices)
    # Auth service returns {"user_id": ..., "email": ...}
    auth_id = data.get("user_id") or data.get("id")
    return {"id": auth_id, "email": data.get("email")}


# ---------------- GET OWN PROFILE ----------------
@router.get("/me", response_model=UserRead)
async def read_own_profile(
    current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Return user profile.
    If full_name is not set, fallback to email from Auth Service.
    """

    auth_user_id = current_user["id"]
    service = UserService(db)

    profile = await service.get_profile_by_auth_user_id(auth_user_id)

    # Lazy profile creation (Just-In-Time provisioning)
    if not profile:
        profile = await service.create_profile(auth_user_id)

    display_name = profile.full_name or current_user.get("email")

    return UserRead(
        id=profile.id,
        auth_user_id=profile.auth_user_id,
        full_name=display_name,
        created_at=profile.created_at,
    )

