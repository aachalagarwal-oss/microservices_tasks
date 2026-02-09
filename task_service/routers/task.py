from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from typing import List
from core.config import settings
from core.database import get_db
from services.task_service import TaskService
from schemas.task import TaskResponse,TaskStatus,TaskCreate

router = APIRouter(prefix="/tasks", tags=["Tasks"])
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



# ---------------- CREATE TASK ----------------
@router.post('/', status_code=201)
async def create_tasks(request: TaskCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = TaskService(db)
    return await service.create_task(
        title=request.title,
        description=request.description,
        status=request.status,
        user_id=user["id"]
    )



@router.get('/', response_model=List[TaskResponse])
async def get_tasks(user:dict = Depends(get_current_user),db: AsyncSession =Depends(get_db),offset: int = 1, limit: int = 10):
    try:
        service=TaskService(db)
        return await service.get_task(user_id=user["id"], limit=limit, offset=offset)
    

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tasks"
        )


@router.get('/{id}')
async def get_tasks(id:int,user:dict = Depends(get_current_user),db: AsyncSession =Depends(get_db)):
    try:
        service=TaskService(db)
        my_tasks=await service.get_task_by_id(user_id=user["id"],id=id)
        return my_tasks
    

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch task"
        )
    

    



@router.put('/{id}')
async def update(request:TaskCreate,id:int,user:dict = Depends(get_current_user),db: AsyncSession =Depends(get_db)):
    try:
        service=TaskService(db)
        return await service.update_task(id=id,user_id=user["id"],title=request.title,description=request.description,status=request.status)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )





@router.delete('/{id}')
async def delete(id:int,user:dict = Depends(get_current_user),db: AsyncSession =Depends(get_db)):
    try:
        service=TaskService(db)
        return await service.delete_task(user_id=user["id"],id=id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )





