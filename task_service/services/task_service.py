from sqlalchemy import select, update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.task_profile import Task

class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db    

    async def create_task(self, title, description, status, user_id):
        task = Task(title=title, description=description, status=status, user_id=user_id)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task(self, user_id: int, limit: int = 10, offset: int = 0):
        result = await self.db.execute(
            select(Task).where(Task.user_id == user_id).limit(limit).offset(offset)
        )
        tasks = result.scalars().all()
        return tasks

    async def get_task_by_id(self, user_id: int, id: int):
        result = await self.db.execute(
            select(Task).where(Task.user_id == user_id, Task.id == id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail=f"No task with id {id} found")
        return task

    async def update_task(self, id: int, user_id: int, title: str = None, description: str = None, status: str = None):
        task = await self.get_task_by_id(user_id, id)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, user_id: int, id: int):
        task = await self.get_task_by_id(user_id, id)
        # Delete using session.delete() which is synchronous
        self.db.delete(task)
        await self.db.commit()
        return {"message": "Task deleted successfully", "task_id": id}
