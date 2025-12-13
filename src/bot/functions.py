from aiogram.enums.chat_member_status import ChatMemberStatus
import re
from datetime import datetime, timedelta
from typing import Optional

async def is_admin(message, bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    bot = await bot.get_chat_member(message.chat.id, bot.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or bot.status != ChatMemberStatus.ADMINISTRATOR:
        return False
    return True

_TIME_UNITS = {
    "minutes": ["минута", "минуту", "минут", "мин", "м", "minutes", "minute", "min", "m"],
    "hours": ["часов", "часа", "час", "ч", "hours", "hour", "h"],
    "days": ["дней", "день", "дня", "д", "days", "day", "d"],
    "weeks": ["неделя", "недели", "недель", "нед", "н", "weeks", "week", "w"],
    "months": ["месяц", "месяца", "месяцев", "мес", "months", "month", "mon"],
    "years": ["лет", "года", "год", "г", "years", "year", "y"],
}

_TIMEDELTA_KWARGS = {
    "minutes": lambda v: {"minutes": v},
    "hours": lambda v: {"hours": v},
    "days": lambda v: {"days": v},
    "weeks": lambda v: {"weeks": v},
    "months": lambda v: {"days": v * 31},
    "years": lambda v: {"days": v * 365},
}

def parse_time(time: Optional[str]) -> Optional[datetime]:
    if not time:
        return None

    time_match = re.match(r"(\d+)([a-z])", time.lower().strip())
    if not time_match:
        return None

    value = int(time_match.group(1))
    unit = time_match.group(2)

    time_unit_category = None
    for category, units in _TIME_UNITS.items():
        if unit in units:
            time_unit_category = category
            break

    if time_unit_category is None:
        return None

    timedelta_kwargs = _TIMEDELTA_KWARGS[time_unit_category](value)
    time_delta = timedelta(**timedelta_kwargs)
    future_datetime = datetime.now() + time_delta

    return future_datetime