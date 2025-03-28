from pydantic import BaseModel
from typing import List, Literal

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatHistory(BaseModel):
    company: Literal['HDB', 'INFY', 'LICI.NS']
    messages: List[ChatMessage]