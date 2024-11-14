import os
import asyncio
from dotenv import load_dotenv
from asyncinit import asyncinit
from Services import ServiceInterface
from src.Helpers import Response
from src.VectorDB.ChromVDB import ChromaVectorDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate


load_dotenv()

@asyncinit
class ChatbotService(ServiceInterface):
    async def __init__(self):
        await super().__init__()

        self.gemini_LLM = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.collection = await ChromaVectorDatabase().__get_collection()
        self.system_template = """
        Answer the user's questions based on the below context. 
        If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

        <context>
        {context}
        </context>
        """
        self.memory =  ConversationBufferWindowMemory(k=5)    
        self.prompt_template = ChatPromptTemplate.from_messages(
            [( "system",self.system_template.format(context=context)),
             ("human","{user_input}"),
            MessagesPlaceholder(variable_name="messages"),
            ]
         )

    # async def make_rag_prompt(self,context):
        
    async def fetch_context_from_db(self, user_input: str, top_k: int = 5) -> str:
        """
        Retrieves the most relevant context from the Chroma vector database
        based on the user input.

        Args:
            user_input (str): The input from the user.
            top_k (int): The number of relevant documents to retrieve.

        Returns:
            str: A concatenated string of relevant context from the database.
        """
        results = await self.collection.query(query_texts=user_input, n_results=top_k)
        context = "\n".join(result["text"] for result in results if "text" in result)
        print(context)
        return context

    async def build_rag_chain(self):
        self.rag_chain = (
            {
                "context": self.fetch_context_from_db,  # Retrieve and format context
                "messages": self.memory,
                "user_input": RunnablePassthrough()
            }
            | self.prompt_template
            | self.gemini_LLM
            | StrOutputParser()  
            )
        return self.rag_chain
    
    async def run(self, question: str):
        """Runs the chatbot by processing the user question through the RAG chain."""
        # Step 1: Build the RAG chain
        rag_chain = await self.build_rag_chain()

        # Step 2: Execute the chain with input data
        response = await rag_chain.invoke(question)

        # Step 3: Save user-bot exchange to memory
        self.memory.save_context({"user_input": question}, {"response": response})

        return response
    
async def main():
    # Initialize the chatbot service
    chatbot = await ChatbotService()

    print("Welcome to the Chatbot! Type 'exit' to quit.")
    
    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Run the chatbot with the user's question
        response = await chatbot.run(user_input)
        
        # Display the response
        print(f"Chatbot: {response}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())