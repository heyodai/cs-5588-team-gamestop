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

# Message model using Pydantic for data validation
class Message(BaseModel):
    id: Optional[str] = None
    text: str

# In-memory storage for messages
messages: List[Message] = []

@app.get("/messages/", response_model=List[Message])
async def get_messages():
    return messages

@app.post("/send/", response_model=Message)
async def send_message(message: Message):
    message.id = str(uuid.uuid4())  # Assign a unique ID to each message
    messages.append(message)
    return message
