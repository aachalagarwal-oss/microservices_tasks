from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from models.user_profile import UserProfile


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile_by_auth_user_id(self, auth_user_id: int) -> UserProfile | None:
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.auth_user_id == auth_user_id)
        )
        profile = result.scalars().first()
        return profile

    async def create_profile(self, auth_user_id: int, full_name: str | None = None) -> UserProfile:
        profile = UserProfile(auth_user_id=auth_user_id, full_name=full_name)
        self.db.add(profile)
        try:
            await self.db.commit()
            await self.db.refresh(profile)
            return profile
        except IntegrityError:
            # Another request/process created the profile concurrently.
            await self.db.rollback()
            existing = await self.get_profile_by_auth_user_id(auth_user_id)
            if existing:
                return existing
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create profile due to concurrent insert"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create profile: {str(e)}"
            )
