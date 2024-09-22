from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid

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

@app.get("/messages/", response_model=List[Message])
async def get_messages():
    return messages

@app.post("/send/", response_model=List[Message])
async def send_message(message: Message):
    # Assign unique ID to user message
    message.id = str(uuid.uuid4())
    messages.append(message)

    # Create and append system message
    system_message = Message(
        id=str(uuid.uuid4()),
        text="Hello World",
        author="system"
    )
    messages.append(system_message)

    # Return the updated list of messages
    return messages
