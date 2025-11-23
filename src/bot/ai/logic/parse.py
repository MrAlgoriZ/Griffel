from aiogram import types

def parse_msg(message: types.Message) -> str:
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ""
    parsed_msg = f"{first_name} {last_name}: {message.text.strip()};"
    print(parsed_msg)
    return parsed_msg