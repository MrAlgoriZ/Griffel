from aiogram.types import Message


class MessageParser:
    @staticmethod
    def _extract_text(msg: Message) -> str:
        if msg.text:
            return msg.text.strip()
        if msg.caption:
            return msg.caption.strip()

        if msg.voice:
            return "Voice message"
        if msg.photo:
            return "Photo"
        if msg.video:
            return "Video"
        if msg.document:
            return "Document"

        return "Unknown message"

    @staticmethod
    def _message_to_dict_single(msg: Message) -> dict:
        return {
            "user": {
                "id": msg.from_user.id,
                "full_name": msg.from_user.full_name,
            },
            "text": MessageParser._extract_text(msg),
        }

    @staticmethod
    def message_to_dict(message: Message) -> dict:
        result = MessageParser._message_to_dict_single(message)

        if message.reply_to_message:
            result["reply"] = MessageParser._message_to_dict_single(
                message.reply_to_message
            )

        return result

    @staticmethod
    def dict_to_text(data: dict, with_id: bool = False) -> str:
        def format_msg(msg: dict) -> str:
            if with_id:
                return (
                    f"{msg['user']['full_name']} ({msg['user']['id']}): {msg['text']}"
                )
            return f"{msg['user']['full_name']}: {msg['text']}"

        current = format_msg(data)

        if reply := data.get("reply"):
            return f"{current}->{format_msg(reply)}"

        return current

    @staticmethod
    def message_to_text(message: Message, with_id: bool = False) -> str:
        return MessageParser.dict_to_text(
            MessageParser.message_to_dict(message), with_id=with_id
        )
