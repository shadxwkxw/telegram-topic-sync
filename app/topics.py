"""Работа с форумными темами: получение и создание."""

from telethon import TelegramClient
from telethon.tl import functions


async def get_topics(client: TelegramClient, chat):
    """Список форумных тем чата. Каждая тема имеет .id, .title, .icon_color, .icon_emoji_id."""
    result = await client(
        functions.messages.GetForumTopicsRequest(
            peer=chat, offset_date=0, offset_id=0, offset_topic=0, limit=100
        )
    )
    return result.topics


async def create_topic(client: TelegramClient, chat, title, icon_color=None, icon_emoji_id=None):
    """Создать тему в чате. Требует Telegram Premium для user-аккаунтов."""
    r = await client(
        functions.messages.CreateForumTopicRequest(
            peer=chat,
            title=title,
            icon_color=icon_color,
            icon_emoji_id=icon_emoji_id,
        )
    )
    for u in r.updates:
        if hasattr(u, "message") and hasattr(u.message, "id"):
            return u.message.id
    raise RuntimeError("topic id not found")
