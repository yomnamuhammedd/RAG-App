import os
import io
import PyPDF2
from typing import List
from dotenv import load_dotenv
from asyncinit import asyncinit
from fastapi import UploadFile
from src.Helpers import Response
from langchain_core.documents import Document
from src.VectorDB.ChromVDB import ChromaVectorDatabase
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .service_interface import ServiceInterface
# from langchain_ai21 import AI21SemanticTextSplitter

load_dotenv()
@asyncinit
class DocumentService(ServiceInterface):
    async def __init__(self):
        await super().__init__()
        self.__vector_database = await ChromaVectorDatabase.get_instance()
        self.__text_splitter = None
        self.size_scale = 1048576
        # self.semantic_text_splitter_chunks = AI21SemanticTextSplitter(chunk_size=1000)

    async def validate_uploaded_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False,Response.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_SIZE_LIMIT * self.size_scale:
            return False,Response.FILE_SIZE_LIMIT_EXCEEDED.value
        
        return True,Response.FILE_VALIDATED_SUCCESS.value
    
    async def get_file_content(self,file:UploadFile):
        try:
            file_content = await file.read()  # Read file content
            return file_content
        except Exception as e:
           return None
    
    async def process_uploaded_file(self,file:UploadFile):
        file_content = await self.get_file_content(file)

        if file.filename.endswith('.pdf'):
            text = await self.extract_text_from_pdf(file_content)
            texts = await self.split_pdf(text) 
            return texts
        
        elif file.filename.endswith('.txt'):
            text = file_content.decode('utf-8')
            texts = await self.split_text(text)
            return texts
        
    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        # Wrap bytes in a BytesIO object to make it file-like
        with io.BytesIO(file_content) as file_stream:
            reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    async def split_text(self, text: str, chunk_size: int = 512) -> List[str]:
        self.__text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=True
            )
        
        texts = self.__text_splitter.split_text(text)
        return texts
    
    async def split_pdf(self, text: str, chunk_size: int = 1500) -> List[Document]:
        self.__text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=500,
            length_function=len,
            is_separator_regex=True
            )
        
        docs = self.__text_splitter.create_documents([text])
        splitted_docs = self.__text_splitter.split_documents(docs)

        return splitted_docs
    
    async def store_to_vectordb(self, texts):
        number_of_inserted_chunks = 0
        for text in texts:
        # If using Document objects, extract the text content
            if isinstance(text, Document):
                text_content = text.page_content
            else:
                text_content = text  
            response = await self.__vector_database.insert_text(text_content) 
            number_of_inserted_chunks+=1
        return response,number_of_inserted_chunks

    async def run(self,file:UploadFile):
        splitted_text = await self.process_uploaded_file(file)
        response,num_chunks = await self.store_to_vectordb(splitted_text)

        return response,num_chunks


        

                                    



