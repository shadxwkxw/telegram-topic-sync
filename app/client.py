"""Фабрика TelegramClient с настройками из `app.config`."""

from telethon import TelegramClient

from app.config import API_HASH, API_ID, SESSION_NAME


def build_client() -> TelegramClient:
    """Возвращает TelegramClient, читающий/создающий сессию рядом с проектом."""
    return TelegramClient(SESSION_NAME, API_ID, API_HASH)
