from fastapi import FastAPI,APIRouter,Depends,status
from fastapi.responses import JSONResponse
from src.Helpers.config import get_settings,Settings
import os
import asyncio

base_router = APIRouter()


@base_router.get("/")
async def weclome(app_settings:Settings = Depends(get_settings)):
    app_settings = get_settings()
    app_name = app_settings.APP_NAME
    
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"Messege":f"Welcome to {app_name} Project"})
