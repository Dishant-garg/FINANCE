from fastapi import APIRouter, HTTPException
from src.Models.chat import ChatHistory, ChatMessage
from src.Services.chat import ChatResponseService

router = APIRouter()

@router.post("/chat", response_model=ChatHistory)
async def process_chat(chat_history: ChatHistory):
    try:
        # Get response from chat service
        response_text = await ChatResponseService.chat_response(chat_history)
        
        # Create bot response
        bot_response = ChatMessage(
            role="assistant",
            content=response_text
        )
        
        # Append bot response to chat history
        chat_history.messages.append(bot_response)
        
        return chat_history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))