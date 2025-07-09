from fastapi import FastAPI
from api.v1.endpoints import java_service

app = FastAPI()
app.include_router(java_service.router, prefix="/api/v1", tags=["Java Services"])
