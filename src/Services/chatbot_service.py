import os
import asyncio
from dotenv import load_dotenv
from asyncinit import asyncinit
from .service_interface import ServiceInterface
from ..VectorDB.ChromVDB import ChromaVectorDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough,Runnable
from langchain.memory import ConversationBufferWindowMemory

load_dotenv()
@asyncinit
class ChatbotService(ServiceInterface):
    async def __init__(self):
        await super().__init__()

        self.gemini_LLM = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.collection = await ChromaVectorDatabase.get_instance()
        
        self.template = """
            Answer the user's questions based on the context and the previous history (memory) provided. 
            If neither contains any relevant information to the question, don't make something up and just say "I don't know":
            <memory>
            {memory}
            </memory>
            <context>
            {context}
            </context>
            <user_question>
            {user_question}
            </user_question>
            """
        self.prompt = PromptTemplate(
            input_variables=["memory","context","user_question"], template=self.template )
        self.memory =  ConversationBufferWindowMemory(k=5)   
        self.prompt_template = ChatPromptTemplate.from_messages(
            [( "system",self.template),
             ("human","{user_input}")] ) 
        
    async def fetch_context_from_db(self, user_input: str, top_k: int = 5) -> str:
        """
        Retrieves the most relevant context from the Chroma vector database based on the user input.
        Args:
            user_input (str): The input from the user.
            top_k (int): The number of relevant documents to retrieve.
        Returns:
            str: A concatenated string of relevant context from the database.
        """
        results =  self.collection.query(query_texts=user_input, n_results=top_k)
        documents = [str(doc) for doc in results['documents'] if doc]
        return documents
        # return  results['documents']
    
    async def format_context(self,user_input):
        documents = await self.fetch_context_from_db(user_input)
        formatted_docs = "\n\n".join(doc for doc in documents if doc)
        return formatted_docs

    async def build_rag_chain(self):
        self.rag_chain = self.prompt | self.gemini_LLM | StrOutputParser()
        return self.rag_chain
    
    async def run(self, question: str):
        """Runs the chatbot by processing the user question through the RAG chain."""
        context = await self.format_context(question)

        memory_str = self.memory.load_memory_variables({}).get("history", "")
        print(memory_str)
        await self.prompt.aformat(memory=memory_str,context=context,user_question=question)

        rag_chain = await self.build_rag_chain()
        response = await rag_chain.ainvoke({"memory": memory_str, "context": context, "user_question": question})
        
        self.memory.save_context({"user_input": question}, {"response": response})

        return response
    
async def main():
    chatbot = await ChatbotService()
    context = await chatbot.format_context("What is CNN?")

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

if __name__ == "__main__":
    asyncio.run(main())