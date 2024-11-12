import os
from fastapi import APIRouter,UploadFile,File,HTTPException
from Services.document_service import DocumentService
from Helpers.Enums.response import ResponseStatus, ResponseMessage,ErrorType
from pydantic import BaseModel

document_upload_router = APIRouter()

class DocumentUploadResponse(BaseModel):
    status: ResponseStatus
    message: ResponseMessage

class ErrorResponse(BaseModel):
    error: ErrorType
    detail: str

UPLOAD_DIR = "./uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@document_upload_router.post("/upload")
async def upload_document(file:UploadFile = File(...)):
    document_service = await DocumentService()

    if file.content_type not in ["application/pdf","text/plain"]:
        raise HTTPException(status_code=400,detail="Only Text inputs and PDFs are allowed") 
    
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process the file using DocumentService
        result = await document_service.run(file_path)

        # After processing, delete the file
        os.remove(file_path)

        return DocumentUploadResponse(
            status=ResponseStatus.SUCCESS, 
            message=ResponseMessage.FILE_UPLOADED
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR)
    

      