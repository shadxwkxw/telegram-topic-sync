"""Выводит список форумных тем для указанного чата."""

import sys

from app.client import build_client
from app.config import DST, SRC
from app.topics import get_topics


def resolve_peer(arg: str) -> int:
    """Возвращает id чата по метке 'src' или 'dst'."""
    arg = arg.lower()
    if arg == "src":
        return SRC
    if arg == "dst":
        return DST
    raise SystemExit("usage: python scripts/list_topics.py [src|dst]")


async def run(peer: int) -> None:
    """Печатает id и название каждой форумной темы указанного чата."""
    topics = await get_topics(client, peer)
    for t in topics:
        print(t.id, "|", t.title)


if len(sys.argv) != 2:
    raise SystemExit("usage: python scripts/list_topics.py [src|dst]")

target_peer = resolve_peer(sys.argv[1])
client = build_client()

with client:
    client.loop.run_until_complete(run(target_peer))
