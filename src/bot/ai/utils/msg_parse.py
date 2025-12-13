from aiogram.types import Message
import re


class MessageParser:
    @staticmethod
    def parse(message: Message) -> str:
        def one_message_parse(msg):
            first_name = msg.from_user.first_name
            last_name = (
                msg.from_user.last_name if msg.from_user.last_name is not None else ""
            )
            full_name = f"{first_name} {last_name}".strip()

            if msg.text or msg.caption:
                text = msg.text.strip() if msg.text else ""
            else:
                kind = (
                    "Voice message"
                    if msg.voice
                    else "Photo"
                    if msg.photo
                    else "Video"
                    if msg.video
                    else "Document"
                    if msg.document
                    else "Unknown message"
                )
                text = kind

            return f"{full_name}: {text}"

        current_msg = one_message_parse(message)

        if message.reply_to_message is not None:
            replied_msg = one_message_parse(message.reply_to_message)
            result = f"{current_msg}->{replied_msg}"
        else:
            result = current_msg

        return result


class ResponseProcessor:
    @staticmethod
    def process(text: str) -> str:
        text = re.sub(r"^(\s*)- ", r"\1• ", text, flags=re.MULTILINE)
        
        text = re.sub(r"^### (.*)", r"📌 \1", text, flags=re.MULTILINE)
        text = re.sub(r"^## (.*)", r"📍 \1", text, flags=re.MULTILINE)
        text = re.sub(r"^# (.*)", r"🏷️ \1", text, flags=re.MULTILINE)
        
        text = re.sub(r"\b(question|ask)\b", r"❓ \1", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(answer|reply)\b", r"💡 \1", text, flags=re.IGNORECASE)
        text = re.sub(
            r"\b(example|for instance)\b", r"🔍 \1", text, flags=re.IGNORECASE
        )
        text = re.sub(r"\b(note|important)\b", r"📝 \1", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(warning|caution)\b", r"⚠️ \1", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(success|good)\b", r"✅ \1", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(error|fail)\b", r"❌ \1", text, flags=re.IGNORECASE)
        return text
