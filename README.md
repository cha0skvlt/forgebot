- stage: mvp
  progress: "90%"
  next_task: final_cleanup

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
    - "Отслеживание согласия и визитов (agreed_at, таблица visits)"
        
pending:

- "Команда /post — отправка поста с кнопкой (markup, confirm)"
- "Команда /guests — список гостей (постранично или с фильтром)"
- "Финальный README с описанием всех команд и сборки"
- "Сборка ZIP-архива для заказчика (docker-compose, .env.example, README, инструкции)"
