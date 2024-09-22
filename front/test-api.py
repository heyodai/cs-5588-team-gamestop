"""
This is just a test API to validate Vue.js frontend.

TODO: Remove this once we have a proper testing API.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

# Message model using Pydantic for data validation
class Message(BaseModel):
    id: Optional[str]
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
