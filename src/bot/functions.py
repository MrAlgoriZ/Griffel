from aiogram.enums.chat_member_status import ChatMemberStatus
import re
from datetime import datetime, timedelta

async def is_admin(message, bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    bot = await bot.get_chat_member(message.chat.id, bot.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or bot.status != ChatMemberStatus.ADMINISTRATOR:
        return False
    return True

def parse_time(time: str | None):
    if not time:
        return None
    
    re_match = re.match(r"(\d+)([a-z])", time.lower().strip())
    now_datetime = datetime.now()

    minutes = ["минута", "минуту", "минут", "мин", "м", 
               "minutes", "minute", "min", "m"]
    
    hours = ["часов", "часа", "час", "ч"
             "hours", "hour" "h"]
    
    days = ["дней", "день", "дня", "д", 
            "days", "day", "d"]
    
    weeks = ["неделя", "недели", "недель", "нед", "н",
             "weeks", "week", "w"]
    
    months = ["месяц", "месяца", "месяцев", "мес", 
              "months", "month", "mon"]
    
    years = ["лет", "года", "год", "г",
             "years", "year", "y"]

    if re_match:
        value = int(re_match.group(1))
        unit = re_match.group(2)

        if unit in minutes: time_delta = timedelta(minutes=value)
        elif unit in hours: time_delta = timedelta(hours=value)
        elif unit in days: time_delta = timedelta(days=value)
        elif unit in weeks: time_delta = timedelta(weeks=value)
        elif unit in months: time_delta = timedelta(days=value * 31)
        elif unit in years: time_delta = timedelta(days=value * 365)
        else: return None
    else:
        return None
    
    new_datetime = now_datetime + time_delta
    return new_datetime