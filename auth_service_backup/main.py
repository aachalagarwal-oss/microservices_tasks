from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Auth Service Running"}

