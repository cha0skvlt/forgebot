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

- 📲 **Один QR-код на стене**
  - Генерируется через `/genqr`
  - Гости сканируют → бот сохраняет Telegram и визит
  - При первом визите: выдаёт инвайт в канал и фиксирует согласие с правилами технеики безопасности и обработку персональных данных.

- 📝 **Ручная регистрация**
  - Команда `/reg`
  - Для гостей без Telegram

- 📊 **Учёт посещений**
  - Каждый визит логируется
  - Повторные визиты считаются

- 📦 **Отчётность**
  - Команда `/report`
  - Выдаёт краткую статистику в Telegram + Excel-файл

- 🔐 **Система админов**
  - `OWNER_ID` и пользователи из таблицы `admins`
  - Только они могут использовать `/reg`, `/genqr`, `/report`

---

## 📜 Команды

#### 👥 Все
- `/start <uuid>` — регистрация по QR, фиксация визита и согласия

#### 🔐 Админы
- `/genqr` — сгенерировать один общий QR
- `/reg ФИО, телефон, YYYY-MM-DD` — вручную зарегистрировать гостя
- `/report` — отчёт в Telegram + Excel-файл

---

## 🐳 Быстрый запуск (Docker)

### 1. Подготовь `.env`

```env
BOT_TOKEN=...
OWNER_ID=123456789
CHANNEL_ID=-100xxxxxxxxx
POSTGRES_DSN=postgresql://forge:forge@db/forge
```

> Используй `.env.example` как шаблон

### 2. Запусти

```bash
docker-compose up --build -d
```

---

## 🧪 Тесты

```bash
docker exec -it forgebot pytest
```
