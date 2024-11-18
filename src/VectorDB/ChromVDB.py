import chromadb
import os
import chromadb.utils.embedding_functions as embedding_functions
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.Helpers.Enums.ResponseEnum import Response
from dotenv import load_dotenv

load_dotenv()
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        genai.configure(api_key="AIzaSyCfdpg3fCA1zfIgC-YeXijDhq3H7xsPfyo")
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model, content=input, task_type="retrieval_document", title=title)["embedding"]
class ChromaVectorDatabase:
    __instance = None

    @classmethod    
    async def get_instance(cls): 
        """
        Class method to connect the chroma db client.
        Creates an a singelton instance of chroma vector database and connects to the chroma persistent client
        """
        if cls.__instance is None:
            cls.__instance = super(ChromaVectorDatabase, cls).__new__(cls)
            cls.__instance.__client = None
            cls.__instance.__collection_name = os.getenv('COLLECTION_NAME')
            cls.__instance.collection = None
            cls.__instance.__embedding_model = GeminiEmbeddingFunction()  
            
            await cls.__instance.__connect__()
        return cls.__instance.__collection

    async def __connect__(self):
        try: 
            self.__client = chromadb.PersistentClient(path='src/VectorDB/')  
            print("Connected to Chroma Vector Database Client")
        except Exception as error:
            print("Failed to connect to ChromaDB client:", error)
        
        # Create the collection if does not exist (i.e database table that will store embeddings for images and texts)
        try:
            self.__collection = self.__client.get_or_create_collection(
                name=self.__collection_name,
                embedding_function=self.__embedding_model
            )
            print(f"Collection '{self.__collection_name}' created with gemini embedding model.")
        except Exception as e:
            print(f"Failed to create {self.__collection_name}: {e}")

