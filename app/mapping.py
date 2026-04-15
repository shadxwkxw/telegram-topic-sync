"""Загрузка маппинга форумных тем из `topic_mapping.json`."""

import json
from pathlib import Path

MAPPING_PATH = Path(__file__).resolve().parent.parent / "topic_mapping.json"


def load_mapping() -> dict[int, int]:
    """Загружает маппинг src_topic_id -> dst_topic_id из topic_mapping.json.

    Формат файла — JSON-объект со строковыми ключами (ограничение JSON):
        {"49": 2, "13012": 3, ...}

    Пары со значением null пропускаются (тема не переносится).
    """
    if not MAPPING_PATH.exists():
        raise SystemExit(
            f"{MAPPING_PATH.name} не найден. Сгенерируй его: " f"python scripts/build_mapping.py"
        )

    raw = json.loads(MAPPING_PATH.read_text())
    return {int(src): int(dst) for src, dst in raw.items() if dst is not None}
