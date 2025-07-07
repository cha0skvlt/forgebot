<h1 align="center">🛡️ ForgeBot</h1>
<p align="center">
  Telegram-бот для регистрации гостей в кузнице через один общий QR-код. Отслеживает визиты и высылает инвайт в канал.
</p>

### @cha0skvlt


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/Aiogram-3.x-blueviolet?logo=telegram" />
  <img src="https://img.shields.io/badge/PostgreSQL-asyncpg-336791?logo=postgresql" />
  <img src="https://img.shields.io/badge/Docker-ready-0db7ed?logo=docker" />
  <img src="https://img.shields.io/badge/License-private-black" />
</p>

---

## 🚀 Функционал

### ✅ QR-регистрация (один код)

- Админ генерирует **один QR-код** через `/genqr`
- Код вешается в кузне
- Каждый гость сканирует его → бот регистрирует Telegram ID, имя и фиксирует **согласие**
- При первом визите бот высылает приватную ссылку на Telegram-канал

### 📝 Ручная регистрация `/reg`

> Формат: `/reg Иванов Иван, +79991234567, 1990-01-01`

- Только для админов
- Сохраняет имя, телефон, дату рождения
- Автоматически создаётся визит

### 🧾 Учёт визитов

- Каждый визит логируется
- При повторном визите бот пишет: `Это уже N-е посещение`

### 🔐 Админ-защита

- `OWNER_ID` — полный доступ
- Дополнительные админы — через таблицу `admins`
- Только админы могут использовать `/reg`, `/genqr`

---

## 🐳 Быстрый запуск (Docker)

### ⚙️ Шаг 1. Подготовь `.env`

```env
BOT_TOKEN=your_token
OWNER_ID=123456789
CHANNEL_ID=-100xxxxxxxxx
POSTGRES_DSN=postgresql://forge:forge@db/forge
```

> Можно взять шаблон: `.env.example`

---

### 🏗️ Шаг 2. Запусти

```bash
docker-compose up --build -d
```

---

## 🧪 Тесты

```bash
docker exec -it forgebot pytest
```

---

## 📁 Структура проекта

```
.
├── bot.py                  # Точка входа
├── modules/                # Все команды и логика
│   ├── admin.py
│   ├── qr.py
│   ├── reqqr.py
│   ├── db.py
│   ├── env.py
│   └── report.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

