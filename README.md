<h1 align="center">🛡️ ForgeBot</h1>
<p align="center">
  Telegram-бот для регистрации гостей по QR-коду. Учитывает визиты, отправляет отчёты и инвайты в канал.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/Aiogram-3.x-blueviolet?logo=telegram" />
  <img src="https://img.shields.io/badge/PostgreSQL-asyncpg-336791?logo=postgresql" />
  <img src="https://img.shields.io/badge/Docker-ready-0db7ed?logo=docker" />
</p>

---

## 🚀 Возможности

### 📲 QR-регистрация
- Один общий QR-код (генерируется через `/genqr`)
- Сканирование = автоматическое согласие с офертой
- Гость регистрируется, фиксируется визит
- При первом визите — инвайт в Telegram-канал

### 📝 Ручная регистрация
- Команда `/reg ФИО, телефон, ДР`
- Для гостей без Telegram
- Добавляет в базу вручную

### 📊 Учёт посещений
- Каждый визит сохраняется (таблица `visits`)
- Счётчик посещений: `Это уже N-е посещение`

### 📦 Отчётность
- Команда `/report`
- Telegram-сводка + Excel-файл

### 🔐 Администрирование
- Команды: `/add_admin`, `/rm_admin`, `/list_admin`
- Только для `OWNER_ID` и назначенных админов
- Приватный доступ к `/reg`, `/genqr`, `/report`
- Команда `/start` для владельца — аптайм и список модулей

---

## ⚙️ Переменные окружения (`.env`)

```env
BOT_TOKEN=123456:ABC...
OWNER_ID=123456789
CHANNEL_ID=-100xxxxxxxxx   # или @forge_channel
POSTGRES_DSN=postgresql://bot:secret@postgres:5432/forgebot
```

---

## 🐳 Быстрый старт (Docker)

```bash
docker-compose up --build -d
```



