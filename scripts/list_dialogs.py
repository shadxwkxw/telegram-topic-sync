"""Выводит список чатов аккаунта с id — нужно для заполнения SRC/DST в .env."""

from app.client import build_client


async def run() -> None:
    """Печатает id и название каждого диалога, доступного аккаунту."""
    async for d in client.iter_dialogs():
        print(d.id, "|", d.name)


client = build_client()

with client:
    client.loop.run_until_complete(run())
