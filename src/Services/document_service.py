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

load_dotenv()
@asyncinit
class DocumentService(ServiceInterface):
    async def __init__(self):
        await super().__init__()
        self.__collection = await ChromaVectorDatabase.get_instance()
        self.size_scale = 1048576
        self.__text_splitter =  RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=650,
            length_function=len,
            is_separator_regex=True
            )
       
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
        texts = self.__text_splitter.split_text(text)
        return texts
    
    async def split_pdf(self, text: str, chunk_size: int = 1500) -> List[Document]:
        docs = self.__text_splitter.create_documents([text])
        splitted_docs = self.__text_splitter.split_documents(docs)

        return splitted_docs
    
    async def insert_text_to_vector_db(self,text:str):
            """
            Insert text data into the Chroma vector database.
            Args:
                text: The text data to be inserted.
            """

            print(f"Text to be added:\n{text}")
            print(f"Type of text: {type(text)}")
            if self.__collection is None:
                raise Exception("Collection is not initialized.")
            
            current_doc_count = self.__collection.count()
            print(f"Number of documents in vector database is {current_doc_count}")
            
            # Get the next id to insert to map it to the current text to be inserted
            next_id = str(int(current_doc_count) + 1)  # Convert to string if IDs are strings
            print(f"ID of current text to be inserted will be {next_id}")

            # Check if the next id is present in the vector database
            existing_ids = self.__collection.get(ids=[next_id])
            print(len(existing_ids['ids']))

            # # If next_id exists, return id already exists response
            if len(existing_ids['ids']) != 0:  
                return Response.TEXT_ID_ALREADY_EXISTS.value
        
            try:
                # Add the text to the chroma collection with the ID and it's metadata
                print("Storing")
                self.__collection.add(
                    ids=[next_id],
                    documents=[text])
                
                return Response.DATA_STORED_SUCCESS.value

            except Exception as error:
                print(error)
                return Response.DATA_STORED_FAILED.value
            
    async def store_to_vectordb(self, texts):
        number_of_inserted_chunks = 0
        for text in texts:
        # If using Document objects, extract the text content
            if isinstance(text, Document):
                text_content = text.page_content
            else:
                text_content = text  
            response = await self.insert_text_to_vector_db(text_content) 
            number_of_inserted_chunks+=1

        return response,number_of_inserted_chunks

    async def run(self,file:UploadFile):
        splitted_text = await self.process_uploaded_file(file)
        response,num_chunks = await self.store_to_vectordb(splitted_text)

        return response,num_chunks


        

                                    



