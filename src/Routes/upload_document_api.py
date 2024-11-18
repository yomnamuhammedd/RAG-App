import os
from fastapi import APIRouter,UploadFile,File,HTTPException,status
from fastapi.responses import JSONResponse
from src.Services.document_service import DocumentService
from src.Helpers.Enums.ResponseEnum import ResponseStatus, ResponseMessage,ErrorType
from pydantic import BaseModel

document_upload_router = APIRouter()

@document_upload_router.post("/upload")
async def upload_document(file:UploadFile = File(...)):

    document_service = await DocumentService()
    valid,validation_signal = await document_service.validate_uploaded_file(file=file)

    if valid:
       response,num_chunks = await document_service.run(file=file)
       return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"response":response,
                                     "number of chunks inserted": num_chunks} )
    else:
     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal":validation_signal} )
        
  
    

      