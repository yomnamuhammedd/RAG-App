import streamlit as st
import requests
import mimetypes
import time
from dotenv import load_dotenv
from src.Helpers.config import get_settings,Settings
import os

app_settings = get_settings()
FAST_API_URL=app_settings.FAST_API_URL
print(f"Fast API URL {FAST_API_URL}")

# Function to stream chatbot responses
def response_generator(bot_message):
    for word in bot_message.split("\n"):
        yield word + " \n"
        time.sleep(0.005)

# Sidebar for selecting the feature
st.sidebar.title("Choose an Action")
app_mode = st.sidebar.selectbox("Select Mode", ["Upload Document", "Chat with Chatbot"])


if "messages" not in st.session_state:
    st.session_state.messages = []

if app_mode == "Upload Document":
    st.title("Upload a Document")
    
    # Document upload interface
    uploaded_file = st.file_uploader("Choose a document file (PDF or TXT)", type=["pdf", "txt"])
    
    if uploaded_file:
        if st.button("Upload"):
            # Send document to FastAPI upload endpoint
            files = {"file": uploaded_file}
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), mime_type)
            }
            response = requests.post(FAST_API_URL+'/upload', files=files)
            
            # Handle response
            if response.status_code == 200:
                
                data = response.json()
                print(data)
                st.success("Document uploaded successfully!")
                # st.write(f"Number of chunks inserted: {data['number of chunks inserted']}")
            else:
                st.error("Failed to upload document.")
                st.write("Error:", response.json().get("signal", "Unknown error"))

elif app_mode == "Chat with Chatbot":
    st.title("Chat with Chatbot Over Your Docs")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask the chatbot"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        response = requests.post(FAST_API_URL+'/chat', json={"question": prompt})
        
        # Handle response
        if response.status_code == 200:
            data = response.json()
            print(data)
            chatbot_response = data["chatbot_response"]
            with st.chat_message("assistant"):
                output = st.write_stream(response_generator(chatbot_response)) # Stream response in chunks
            # Add chatbot response to chat history
            st.session_state.messages.append({"role": "assistant", "content": chatbot_response})
        else:
            st.error("Failed to get a response from the chatbot.")
            # st.write("Error:", response.json().get("error", "Unknown error"))