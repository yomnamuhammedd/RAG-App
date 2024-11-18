import os
from fastapi import APIRouter,UploadFile,File,HTTPException,status
from fastapi.responses import JSONResponse
from src.Services.document_service import DocumentService
from src.Helpers.Enums.ResponseEnum import Response, ResponseMessage,ErrorType
from src.Services.chatbot_service import ChatbotService
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

chat_api_router = APIRouter()
chatbot_instance = None

@chat_api_router.on_event("startup")
async def initialize_chatbot():
    """Initialize the chatbot instance."""
    global chatbot_instance
    print("Initializing the chatbot service...")
    chatbot_instance = await ChatbotService()
    print("Chatbot service initialized successfully!")
    

@chat_api_router.post("/chat")
async def ask_question(request: QuestionRequest):
    """
    Takes a question from the user and returns the chatbot's response.
    """
    if not chatbot_instance:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={ "response":"Faild to initiliaze Chatbot Service"}
        )
    try:
        # Run the chatbot and get the response
        response = await chatbot_instance.run(request.question)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "chatbot_response": response,
                "response":Response.CHAT_BOT_RESPONSE_SUCCESS.value
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"An error occurred: {str(e)}",
                     "response":Response.CHAT_BOT_RESPONSE_FAILED.value}
        )