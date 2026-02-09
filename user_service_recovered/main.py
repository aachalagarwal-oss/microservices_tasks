from fastapi import FastAPI
from routers import user
from core.database import Base, engine

app = FastAPI(title="User Service")
app.include_router(user.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Check if table exists
# If not → create it