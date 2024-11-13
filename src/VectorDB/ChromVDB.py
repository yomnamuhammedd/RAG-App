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
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model, content=input, task_type="retrieval_document", title=title)["embedding"]
class ChromaVectorDatabase:
    __instance = None

    @classmethod    
    async def get_instance(cls): 
        """
        Class method to get the chroma db client.
        Creates an a singelton instance of chroma vector database and connects to the chroma persistent client
        """
        if cls.__instance is None:
            cls.__instance = super(ChromaVectorDatabase, cls).__new__(cls)
            cls.__instance.__client = None
            cls.__instance.__collection_name = os.getenv('COLLECTION_NAME')
            cls.__instance.__collection = None
            cls.__instance.__embedding_model = GeminiEmbeddingFunction()  
            
            await cls.__instance.__connect__()
        return cls.__instance

    async def __connect__(self):
        """
        Private method to connect to chroma client.
        Intialize Google Embedding model
        Creating the collection to store the embedding for text and pdfs.
        """
       # Connect to chroma persistent client to save the local database to Database/
        try: 
            self.__client = chromadb.PersistentClient(path='src/VectorDB/')  
            print("Connected to Chroma Vector Database Client")
        except Exception as error:
            print("Failed to connect to ChromaDB client:", error)
        
        # Initilaize the Google Embedding Model for embedding text and images
        # try:
        #     self.__embedding_model = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.getenv('API_KEY'))
        #     print("Initialized Google Embedding Model")
        # except Exception as error:
        #     print("Failed to load the Google Embedding model:", error)
        
        # Create the collection if does not exist (i.e database table that will store embeddings for images and texts)
        try:
            self.__collection = self.__client.get_or_create_collection(
                name=self.__collection_name,
                embedding_function=self.__embedding_model
            )
            print(f"Collection '{self.__collection_name}' created with gemini embedding model.")
        except Exception as e:
            print(f"Failed to create {self.__collection_name}: {e}")

    async def insert_text(self,text:str):
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
                
                # If success,return the response text added success
                return Response.DATA_STORED_SUCCESS.value

            # If failed to insert text,return the response text added failure
            except Exception as error:
                print(error)
                return Response.DATA_STORED_FAILED.value
