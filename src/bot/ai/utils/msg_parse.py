from aiogram.types import Message

class MessageParser:
    @staticmethod
    def parse(message: Message) -> str:
        def one_message_parse(msg):
            first_name = msg.from_user.first_name
            last_name = msg.from_user.last_name if msg.from_user.last_name is not None else ""
            full_name = f"{first_name} {last_name}".strip()
            
            if msg.text or msg.caption:
                text = msg.text.strip() if msg.text else ""
            else:
                kind = "Voice message" if msg.voice else \
                    "Photo" if msg.photo else \
                    "Video" if msg.video else \
                    "Document" if msg.document else "Unknown message"
                text = kind

            
            return f"{full_name}: {text}"
        
        current_msg = one_message_parse(message)
        
        if message.reply_to_message is not None:
            replied_msg = one_message_parse(message.reply_to_message)
            result = f"{current_msg}->{replied_msg}"
        else:
            result = current_msg
        
        return result