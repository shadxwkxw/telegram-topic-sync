"""Загрузка переменных окружения из .env и константы миграции."""

import os

from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SRC = int(os.environ["SRC"])
DST = int(os.environ["DST"])

SESSION_NAME = "migrate"
BATCH = 100
SLEEP_BETWEEN_BATCHES = 2
