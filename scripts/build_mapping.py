"""Генерирует topic_mapping.json, сопоставляя темы SRC и DST по названиям.

Темы с совпадающими названиями маппятся автоматически. Темы без совпадения
попадают в файл со значением null — их нужно либо заполнить руками
(прописать id целевой темы), либо оставить null (тогда тема не переносится).

General (id=1) маппится автоматически 1->1 (есть в обеих группах).
"""

import json
from pathlib import Path

from app.client import build_client
from app.config import DST, SRC
from app.topics import get_topics

OUTPUT = Path(__file__).resolve().parent.parent / "topic_mapping.json"


async def run() -> None:
    """Строит маппинг src_topic_id -> dst_topic_id по названиям и пишет его в JSON."""
    src_topics = await get_topics(client, SRC)
    dst_topics = await get_topics(client, DST)

    dst_by_title = {t.title: t.id for t in dst_topics}

    mapping: dict[str, int | None] = {}
    matched: list[tuple[int, int, str]] = []
    unmatched: list[tuple[int, str]] = []

    for t in src_topics:
        dst_id = dst_by_title.get(t.title)
        mapping[str(t.id)] = dst_id
        if dst_id is not None:
            matched.append((t.id, dst_id, t.title))
        else:
            unmatched.append((t.id, t.title))

    mapping = dict(sorted(mapping.items(), key=lambda kv: int(kv[0])))

    print(f"Matched {len(matched)}/{len(src_topics)} topics by title:")
    for src_id, dst_id, title in matched:
        print(f"  {src_id:>6} -> {dst_id:<6}  {title}")

    if unmatched:
        print(f"\n{len(unmatched)} unmatched (dst id = null, fill manually):")
        for src_id, title in unmatched:
            print(f"  {src_id:>6} -> ?       {title}")

    OUTPUT.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    print(f"\nWritten to {OUTPUT.name}")
    if unmatched:
        print("Edit it by hand to fill in missing dst ids (or leave null to skip).")


client = build_client()

with client:
    client.loop.run_until_complete(run())
