from aiogram.types import Message


class MessageParser:
    @staticmethod
    def message_to_text(message: Message) -> str:
        def one_message_parse(msg):
            full_name = msg.from_user.full_name

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
    
    @staticmethod
    def message_to_dict(message: Message) -> dict:
        def one_message_parse(msg):
            full_name = msg.from_user.full_name
            user_id = msg.from_user.id

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

            return {"user": {"full_name": full_name, "id": user_id}, "text": text}
        
        current_msg = one_message_parse(message)

        if message.reply_to_message is not None:
            replied_msg = one_message_parse(message.reply_to_message)
            result = current_msg.update({"reply": replied_msg})
        else:
            result = current_msg

        return result

    @staticmethod
    def dict_to_text(data: dict) -> str:
        def one_message_dict_parse(msg_dict):
            full_name = msg_dict["user"]["full_name"]
            text = msg_dict["text"]
            return f"{full_name}: {text}"

        current_msg = one_message_dict_parse(data)

        reply_part = data.get("reply")

        if reply_part is not None:
            replied_msg = one_message_dict_parse(reply_part)
            result = f"{current_msg}->{replied_msg}"

        else:
            result = current_msg

        return result