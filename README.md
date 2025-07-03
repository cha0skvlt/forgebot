- stage: mvp
  progress: "80%"
  next_task: guests_accept_offer

  completed:
    - "Базовый bot.py (загрузка модулей, /start, логгирование)"
    - "Admin-модуль с командами /add_admin, /rm_admin, /list_admin"
    - "PostgreSQL подключение через db.py"
    - "Логирование в bot.log и stdout"
    - "docker-compose.yml и Dockerfile (базовая версия)"
    - "Формализован договор и структура MVP"
    - "Создание таблицы guests (UUID, tg_id, имя, телефон, ДР, source)"
    - "Реализация QR-регистрации гостей через /start <uuid>"
    - "Ручная регистрация через команду /reg"
    - "Инвайт в Telegram-канал после регистрации"
    - "Генерация и отображение QR-кодов"

  pending:
    - "Подтверждение оферты и логика согласия"
    - "Команды /post, /report, /guests"
    - "Финальный README + передача ZIP с docker-билдом"
