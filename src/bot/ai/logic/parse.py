from pyrogram import Client
from src.utils.env import Env

pyrogram_client = Client(
    "my_bot",
    api_id=Env.TELEGRAM_API,
    api_hash=Env.TELEGRAM_API_HASH,
    bot_token=Env.TELEGRAM
)

async def get_last_messages(chat_id: int, limit: int = 15) -> str:
    try:
        messages = []
        
        async for message in pyrogram_client.get_chat_history(chat_id, limit=limit):
            if message.from_user:
                username = message.from_user.first_name
                if message.from_user.last_name:
                    username += f" {message.from_user.last_name}"
            else:
                username = "Unknown"
            
            content = ""
            if message.text:
                content = message.text
            elif message.caption:
                content = message.caption
            elif message.photo:
                content = "[Фото]"
            elif message.video:
                content = "[Видео]"
            elif message.document:
                content = "[Документ]"
            elif message.sticker:
                content = "[Стикер]"
            elif message.voice:
                content = "[Голосовое]"
            elif message.animation:
                content = "[GIF]"
            elif message.audio:
                content = "[Аудио]"
            else:
                content = "[Медиа]"
            
            messages.append(f"{username}: {content}")
        
        messages.reverse()
        
        return "; ".join(messages)
    
    except Exception as e:
        return f"Ошибка при получении истории: {str(e)}"
