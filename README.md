<h1 align="center">🛡️ ForgeBot</h1>
<p align="center">
  Telegram-бот для регистрации гостей в кузнице по QR-коду. Считает визиты, отправляет отчёты и инвайты.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/Aiogram-3.x-blueviolet?logo=telegram" />
  <img src="https://img.shields.io/badge/PostgreSQL-asyncpg-336791?logo=postgresql" />
  <img src="https://img.shields.io/badge/Docker-ready-0db7ed?logo=docker" />
</p>

---

## 🚀 Возможности

- 📲 **QR-регистрация**
  - Один QR-код для всех, генерируется через `/genqr`
  - Сканирование = автоматическое согласие на оферту
  - Гость добавляется в базу, фиксируется визит
  - Первый визит → инвайт в Telegram-канал

- 📝 **Ручная регистрация**
  - Команда `/reg` для гостей без Telegram
  - Требует: ФИО, телефон, дата рождения

- 📊 **Учёт посещений**
  - Каждый визит сохраняется
  - Повторные считаются отдельно

- 📦 **Отчётность**
  - Команда `/report`
  - Telegram-сводка + Excel-файл

- 🔐 **Администрирование**
  - Только `OWNER_ID` и админы из таблицы `admins`
  - Приватный доступ к функциям `/reg`, `/genqr`, `/report`

---
## 📜 Команды

| Команда                  | Доступ     | Описание                                               |
|--------------------------|------------|--------------------------------------------------------|
| `/start <uuid>`          | Все        | Регистрация по QR-коду и учёт визита                   |
| `/genqr`                 | Админы     | Генерация одного общего QR-кода                        |
| `/reg ФИО, телефон, ДР`  | Админы     | Ручная регистрация гостя без Telegram                  |
| `/report`                | Админы     | Отчёт по гостям: Telegram-сводка                       |
| `/xls`                   | Админы     | Excel-файл с деталями гостей                           |

---

## ⚙️ .env пример

```env
BOT_TOKEN=123456:ABC...
OWNER_ID=123456789
CHANNEL_ID=-100xxxxxxxxx # или forge_channel
POSTGRES_USER=bot
POSTGRES_PASSWORD=secret
POSTGRES_DB=forgebot
POSTGRES_DSN=postgresql://bot:secret@postgres:5432/forgebot
```
При запуске бот сам создаёт таблицы и загружает список админов.

🐳 Быстрый запуск (Docker)

```
docker-compose up --build -d
```
