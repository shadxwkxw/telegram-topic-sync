"""Пересылка сообщений темы из одного чата в тему другого чата."""

import asyncio
import random

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl import functions

from app.config import BATCH, SLEEP_BETWEEN_BATCHES


async def migrate_topic(client: TelegramClient, src, dst, src_topic_id, dst_topic_id):
    """Пересылает все сообщения темы src_topic_id из src в тему dst_topic_id чата dst."""
    print("  collecting message ids...", flush=True)
    ids = []
    async for msg in client.iter_messages(src, reply_to=src_topic_id, reverse=True):
        ids.append(msg.id)
    print(f"  total: {len(ids)} messages", flush=True)

    src_peer = await client.get_input_entity(src)
    dst_peer = await client.get_input_entity(dst)

    for i in range(0, len(ids), BATCH):
        end = i + BATCH
        chunk = ids[i:end]
        while True:
            try:
                await client(
                    functions.messages.ForwardMessagesRequest(
                        from_peer=src_peer,
                        to_peer=dst_peer,
                        id=chunk,
                        random_id=[random.randrange(-(2**63), 2**63) for _ in chunk],
                        top_msg_id=dst_topic_id,
                    )
                )
                print(f"  {i + len(chunk)}/{len(ids)}", flush=True)
                await asyncio.sleep(SLEEP_BETWEEN_BATCHES)
                break
            except FloodWaitError as e:
                print(f"  FloodWait {e.seconds}s", flush=True)
                await asyncio.sleep(e.seconds + 5)
