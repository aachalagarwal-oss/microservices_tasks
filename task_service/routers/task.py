from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from typing import List
from core.config import settings
from core.database import get_db
from services.task_service import TaskService
from schemas.task import TaskResponse, TaskStatus, TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])
security = HTTPBearer()


# ---------------- TOKEN VALIDATION ----------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate token with auth service and return user info
    """
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
    auth_id = data.get("user_id") or data.get("id")
    return {"id": auth_id, "email": data.get("email")}


# ---------------- CREATE TASK ----------------
@router.post("", status_code=201, response_model=TaskResponse)
async def create_task(
    request: TaskCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task for the authenticated user
    """
    service = TaskService(db)
    return await service.create_task(
        title=request.title,
        description=request.description,
        status=request.status,
        user_id=user["id"],
    )


# ---------------- GET ALL TASKS ----------------
@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    """
    Get all tasks for the authenticated user with pagination
    """
    try:
        service = TaskService(db)
        return await service.get_task(user_id=user["id"], limit=limit, offset=offset)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tasks",
        )


# ---------------- GET TASK BY ID ----------------
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single task by ID for the authenticated user
    """
    try:
        service = TaskService(db)
        return await service.get_task_by_id(user_id=user["id"], id=task_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch task",
        )


# ---------------- UPDATE TASK ----------------
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a task by ID
    """
    try:
        service = TaskService(db)
        return await service.update_task(
            id=task_id,
            user_id=user["id"],
            title=request.title,
            description=request.description,
            status=request.status,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task",
        )


# ---------------- DELETE TASK ----------------
@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a task by ID
    """
    try:
        service = TaskService(db)
        return await service.delete_task(user_id=user["id"], id=task_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task",
        )
