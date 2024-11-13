from enum import Enum

class Response(Enum):
    
    FILE_UPLOADED_SUCCESS = "file_uploaded_success"
    FILE_UPLOADED_FAILED = "file_uploaded_Failed"
    FILE_PROCESSING_SUCCESS= "file_processing_Success"
    FILE_PROCESSING_FAILED= "file_processing_Failed"
    FILE_CONTENT_RETRIEVED_SUCCESS = "file_content_retrieved_success"
    FILE_CONTENT_RETRIEVED_FAILED = "file_content_retrieved_failed"


    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_LIMIT_EXCEEDED = "file_size_exceeded"
    FILE_VALIDATED_SUCCESS = "file_validated_succesffully"
    FILE_VALIDATED_FAILED = "file_validated_failed"

    DATA_STORED_SUCCESS = "text_stored_successfully"
    DATA_STORED_FAILED = "text_stored_failed"
    TEXT_ID_ALREADY_EXISTS = "this_id_already_exists_in_vectordatabase"

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