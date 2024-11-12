from enum import Enum

class Response(Enum):
    
    FILE_TYPE_NOT_SUPPORTED = "File_Type_Not_Supported"
    FILE_SIZE_EXCEEDED = "File_Size_Exceeded"
    FILE_UPLOADED_SUCCESS = "File_Uploaded_Success"
    FILE_UPLOADED_FAILED = "File_Uploaded_Failed"
    PROCESSING_SUCCESS= "Processing Success"
    PROCESSING_FAILED= "Processing Failed"

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAIL = "fail"

class ResponseMessage(str, Enum):
    FILE_UPLOADED_SUCCESS = "Document uploaded, processed, and deleted successfully"
    INVALID_FILE_TYPE = "Only Text and PDF files are allowed"
    INTERNAL_ERROR = "An error occurred during file processing"
    UNAUTHORIZED = "Unauthorized access"

class ErrorType(str, Enum):
    BAD_REQUEST = "Bad Request"
    UNAUTHORIZED = "Unauthorized"
    INTERNAL_ERROR = "Internal Server Error"