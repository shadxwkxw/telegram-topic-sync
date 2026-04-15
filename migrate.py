"""Точка входа: переносит все темы согласно topic_mapping.json из SRC в DST."""

from app.client import build_client
from app.config import DST, SRC
from app.mapping import load_mapping
from app.migrator import migrate_topic


async def run() -> None:
    """Пробегается по записям маппинга и переносит каждую тему."""
    topic_mapping = load_mapping()
    print("Mapping:", topic_mapping)
    for src_id, dst_id in topic_mapping.items():
        print(f"Migrating topic {src_id} -> {dst_id}")
        await migrate_topic(client, SRC, DST, src_id, dst_id)


client = build_client()

with client:
    client.loop.run_until_complete(run())
