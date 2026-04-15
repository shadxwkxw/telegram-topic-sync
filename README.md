# tg-migrate

Перенос истории сообщений из одной Telegram-супергруппы с форумными темами в другую. Сообщения пересылаются через `ForwardMessagesRequest` с сохранением авторства (останется плашка *Forwarded from*).

## Возможности

- Пересылка всех сообщений темы в соответствующую тему целевого чата.
- Батчи по 100 сообщений, автоматическая обработка `FloodWaitError`.
- Прогресс по каждой теме в консоли.

## Ограничения

- Оригинальные **даты сообщений не сохраняются** — у пересланных стоит дата пересылки (оригинальная видна по клику на плашку *Forwarded from*).
- **Плашку *Forwarded from* убрать нельзя** без потери авторства — это ограничение Telegram.
- **Reply-цепочки между сообщениями** сохраняются только внутри одного батча из 100 сообщений, ссылки за пределы батча теряются.
- Исходный чат не должен иметь запрета на пересылку (*Restrict saving content*).
- Создание тем через user API требует **Telegram Premium** — поэтому темы в целевом чате создаются вручную через UI, а скрипт только переносит сообщения.

## Требования

- Python 3.11+ (проверено на 3.11).
- Аккаунт Telegram, состоящий в обоих чатах; в целевом — с правом *Manage topics*.
- Целевой чат: супергруппа (id начинается с `-100`) с включёнными темами.
- `api_id` и `api_hash` с [my.telegram.org](https://my.telegram.org) → *API development tools*.

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

`pip install -e .` ставит проект в editable-режиме — скрипты в `scripts/` смогут делать `from app.*` без `sys.path`-хаков.

## Подготовка

1. **Создать `.env`** на основе `.env.example` и подставить свои значения:

   ```bash
   cp .env.example .env
   ```

   Отредактировать `.env`:

   ```
   API_ID=12345
   API_HASH=your_api_hash_here
   SRC=-1001234567890
   DST=-1009876543210
   ```

   `API_ID` и `API_HASH` берутся с [my.telegram.org](https://my.telegram.org) → *API development tools*.

2. **Получить id чатов:**

   ```bash
   python scripts/list_dialogs.py
   ```

   При первом запуске попросит номер телефона и код из Telegram. Сессия сохранится в `migrate.session`, повторно логиниться не придётся.

   Полученные id исходного и целевого чата вписать в `.env` (`SRC` и `DST`).

3. **Посмотреть темы исходного чата:**

   ```bash
   python scripts/list_topics.py src
   ```

4. **Создать такие же темы в целевом чате руками** через Telegram Desktop (`+` в заголовке чата → *Create topic*). **Важно: названия должны совпадать** — скрипт сопоставления ищет темы по точному совпадению заголовков.

5. **Сгенерировать маппинг:**

   ```bash
   python scripts/build_mapping.py
   ```

   Скрипт получит списки тем из обоих чатов, сопоставит их по названиям и запишет в `topic_mapping.json`. В консоли покажет, что совпало, а что нет.

   Если какие-то темы не совпали по названию (`dst id = null`) — открой `topic_mapping.json` и проставь нужные id вручную. Пары со значением `null` пропускаются (не переносятся).

   Пример `topic_mapping.json`:
   ```json
   {
     "1": null,
     "49": 2,
     "13012": 3
   }
   ```

   Повторный запуск `build_mapping.py` **перезапишет** файл — если правил его руками, делай бэкап.

## Запуск

```bash
python migrate.py
```

В консоли будет видно:

```
Migrating topic 49 → 2
  collecting message ids...
  total: 821 messages
  100/821
  200/821
  ...
```

При `FloodWait` скрипт сам подождёт и продолжит.

## Структура проекта

```
.
├── .env                        # ключи и id чатов (не коммитить!)
├── .env.example                # шаблон для .env
├── .gitignore
├── Makefile                    # команды разработки и запуска
├── README.md
├── migrate.py                  # точка входа
├── migrate.session             # кэш авторизации Telethon (создаётся автоматически)
├── topic_mapping.json          # маппинг тем, генерируется build_mapping.py (не коммитить!)
├── topic_mapping.example.json  # шаблон
├── app/
│   ├── __init__.py
│   ├── config.py               # загрузка .env и константы (BATCH, пауза)
│   ├── client.py               # сборка TelegramClient
│   ├── topics.py               # get_topics, create_topic
│   ├── migrator.py             # логика переноса одной темы
│   └── mapping.py              # загрузка topic_mapping.json
├── scripts/
│   ├── list_dialogs.py         # список чатов с id
│   ├── list_topics.py          # список тем в src/dst
│   └── build_mapping.py        # автосопоставление тем по названиям
└── venv/
```

## Настройки

Параметры размера батча и паузы между пачками лежат в [`app/config.py`](app/config.py):

```python
BATCH = 100                   # размер батча форварда (max 100 — ограничение Telegram)
SLEEP_BETWEEN_BATCHES = 2     # пауза в секундах между батчами
```

Если часто ловишь `FloodWait` — увеличь паузу до 4–5 секунд.

## Нюансы при запуске

- **Скрипт без ресюма.** При обрыве и перезапуске перенесёт сообщения по уже пройденным темам заново (будут дубли). Если упало посередине — поменяй в `topic_mapping.json` значения уже готовых тем на `null` перед повторным запуском.
- **Темы без сообщений** занимают по одному сервисному сообщению (создание темы) — это нормально, они не форвардятся.
- **Сервисные сообщения** (добавление участника, смена названия и т. п.) в форвард не попадают — только обычные.

## Troubleshooting

### `ApiIdInvalidError: The api_id/api_hash combination is invalid`

Пара ключей не совпадает с тем, что выдал my.telegram.org. Частые причины:

- в `.env` остались плейсхолдеры из `.env.example`;
- `API_ID` и `API_HASH` перепутаны местами;
- при копировании `API_HASH` затянулись пробелы или кавычки.

После исправления удали `migrate.session` перед повторным запуском.

### `PremiumAccountRequiredError` при создании темы

Telegram требует Premium для создания тем через user API. Обход — создать темы в целевом чате руками через UI, затем сгенерировать маппинг через `python scripts/build_mapping.py`.

### `ImportError: cannot import name 'GetForumTopicsRequest' from 'telethon.tl.functions.channels'`

В свежих версиях Telethon форумные запросы переехали из `functions.channels` в `functions.messages`. Обнови библиотеку:

```bash
pip install --upgrade --force-reinstall telethon
```

Если всё ещё падает, проверь, где живёт класс в твоей версии:

```bash
python -c "
import telethon.tl.functions as f, pkgutil, importlib
for _, name, _ in pkgutil.iter_modules(f.__path__):
    m = importlib.import_module(f'telethon.tl.functions.{name}')
    hits = [x for x in dir(m) if 'Forum' in x]
    if hits: print(name, hits)
"
```

### `TypeError: GetForumTopicsRequest.__init__() got an unexpected keyword argument 'channel'`

В `functions.messages.*` параметр называется `peer`, а не `channel`. Скрипт в репозитории уже использует правильное имя — ошибка возможна только если редактируешь вручную.

### `TypeError: forward_messages() got an unexpected keyword argument 'top_msg_id'` / `'reply_to'`

Высокоуровневый `client.forward_messages()` в ряде версий Telethon вообще не поддерживает таргет форумной темы. Поэтому скрипт использует низкоуровневый `ForwardMessagesRequest` с `top_msg_id` напрямую — он работает во всех версиях 1.28+.

### `ChatForwardsRestricted`

В исходном чате включён запрет на пересылку (*Restrict saving content*). Форвард через API не сработает. Варианты:

- отключить запрет (если ты админ источника);
- переписать скрипт на схему *download media → upload media*, но тогда потеряется автор и будут перезаливаться все файлы.

### `ChatAdminRequiredError`

Аккаунт не админ целевого чата или не имеет права *Manage topics*. Выдай нужные права и перезапусти.

### `FloodWaitError: A wait of N seconds is required`

Это не ошибка, а встроенный rate limit. Скрипт сам ждёт и продолжает — прерывать не надо. Если интервалы слишком длинные, увеличь `SLEEP_BETWEEN_BATCHES` в [`app/config.py`](app/config.py) до 4–5 секунд.

### Terminal "завис" после `Migrating topic ...`

Скрипт жив — для больших тем этап `collecting message ids...` может занимать десятки секунд, в это время прогресс не печатается. Как только появится `total: N messages`, пойдут батчи.

## Разработка

В корне проекта есть `Makefile` с основными командами. Посмотреть все:

```bash
make help
```

Типичный поток:

```bash
make install-dev    # установить проект + линтеры (один раз)
make format         # отформатировать код (black + isort)
make ci             # прогнать все линтеры так же, как CI
```

Команды миграции тоже доступны через make:

```bash
make list-dialogs      # список чатов с id
make list-topics-src   # темы исходного чата
make list-topics-dst   # темы целевого чата
make build-mapping     # сгенерировать topic_mapping.json
make run               # запустить миграцию
```

Конфиги линтеров:

- `pyproject.toml` — `[project]` (зависимости и метаданные пакета) + секции black, isort, mypy, pylint.
- `.flake8` — flake8 (он не читает pyproject).

Все пять инструментов работают **без отключённых правил**: в коде нет `# noqa`, в конфигах нет `disable`/`extend-ignore`. Скрипты в `scripts/` импортируют `app.*` напрямую, потому что проект установлен в editable-режиме (`pip install -e .`).

CI поднят на GitHub Actions — см. `.github/workflows/ci.yml`, прогоняет все пять инструментов на каждом push/PR в `main`.

## Безопасность

`.env` и `migrate.session` — это доступ к аккаунту. Оба исключены в `.gitignore`.
