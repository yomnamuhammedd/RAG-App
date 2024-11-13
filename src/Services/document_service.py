import os
import io
import PyPDF2
from typing import List
from asyncinit import asyncinit
from fastapi import UploadFile
from Helpers import Response
from VectorDB.ChromVDB import ChromaVectorDatabase
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .service_interface import ServiceInterface

@asyncinit
class DocumentService(ServiceInterface):
    async def __init__(self):
        super().__init__()
        self.__vector_database = await ChromaVectorDatabase()
        self.__text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=500,
            length_function=len,
            is_separator_regex=True
        )

    async def validate_uploaded_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False,Response.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_SIZE_LIMIT * self.size_scale:
            return False,Response.FILE_SIZE_LIMIT_EXCEEDED.value
        
        return True,Response.FILE_VALIDATED_SUCCESS.value
    
    async def process_uploaded_file(self,file:UploadFile):
        if file.filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file)
            texts = self.split_pdf_text(text) 
            return Response.FILE_PROCESSING_SUCCESS.value
        
        elif file.filename.endswith('.txt'):
            content = self.get_file_content(file)
            text = content.decode('utf-8')
            texts = self.split_text(text)
            return Response.FILE_PROCESSING_SUCCESS.value
        
        await self.store_to_vectordb(texts)
        return Response.DATA_STORED_SUCCESS.value


                                    



