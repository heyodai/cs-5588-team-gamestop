from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import ollama

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Specifies the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class Message(BaseModel):
    id: Optional[str] = None
    text: str
    author: Optional[str] = "user"


messages: List[Message] = []


def get_assistant_response():
    """
    Generate a response from the assistant using the Ollama API.

    TODO: Make the assistant's role and purpose configurable.
    """
    # Provide a system message to introduce the assistant
    msg_list = [
        {
            "role": "system",
            "content": "You are an informative and helpful stock investment assistant. Your purpose is to provide data-driven insights and balanced advice to users seeking information on stock investments. You should focus on offering clear, factual, and practical investment tips, taking into account historical market data and current trends. Remember, your advice should not be construed as financial advice from a certified expert but as guidance to help users make informed decisions. Always encourage users to consult with a financial advisor for personalized advice.",
        }
    ]

    # Generate a list of previous messages
    for message in messages:
        msg_list.append(
            {
                "role": message.author,
                "content": message.text,
            }
        )

    # Call the Ollama API to generate a response
    response = ollama.chat(
        model="llama3",
        messages=msg_list,
    )

    # Return the assistant's response
    return response["message"]["content"]


@app.get("/messages/", response_model=List[Message])
async def get_messages():
    return messages


@app.post("/send/", response_model=List[Message])
async def send_message(message: Message):
    # Assign unique ID to user message
    message.id = str(uuid.uuid4())
    messages.append(message)

    # Generate a response from the assistant
    response_text = get_assistant_response()

    # Create and append assistant message
    assistant_message = Message(
        id=str(uuid.uuid4()), text=response_text, author="assistant"
    )
    messages.append(assistant_message)

    # Return the updated list of messages
    return messages
