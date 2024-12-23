from fastapi import FastAPI
from dotenv import load_dotenv
from src.Routes import base ,upload_document_api,chat_api

load_dotenv()

app = FastAPI()

app.include_router(base.base_router)
app.include_router(upload_document_api.document_upload_router)
app.include_router(chat_api.chat_api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Slash Chatbot"}