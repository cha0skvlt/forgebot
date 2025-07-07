stage: mvp
progress: "95%"
next_task: generate_readme

completed:
  - "Базовый bot.py (загрузка модулей, /start, логгирование)"
  - "Admin-модуль с командами /add_admin, /rm_admin, /list_admin"
  - "PostgreSQL подключение через db.py"
  - "Логирование в bot.log и stdout"
  - "docker-compose.yml и Dockerfile (базовая версия)"
  - "Формализован договор и структура MVP"
  - "Создание таблицы guests (UUID, tg_id, имя, телефон, ДР, source)"
  - "Реализация QR-регистрации гостей через /start"
  - "Ручная регистрация через команду /reg"
  - "Инвайт в Telegram-канал после регистрации"
  - "Генерация и отображение QR-кодов"
  - "Учёт повторных посещений мастер-классов (таблица visits: guest_id, ts)"
  - "Автоматический ответ при повторном визите (/start): 'Это уже X-е посещение'"
  - "Команда /report — статистика посещений (уникальные, повторные, по дате)"
  - "Подтверждение оферты и логика согласия (поле agreed_at в guests)"
  - "Fallback имени и индекс по visits(guest_id)"

pending:
  - "Финальный README с описанием всех команд и сборки"
  - "Сборка ZIP-архива для заказчика (docker-compose, .env.example, README, инструкции)"
