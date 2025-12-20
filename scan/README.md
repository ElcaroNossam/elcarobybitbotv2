# Crypto Screener

Реал-тайм скринер криптовалют с динамическим обновлением данных через WebSocket.

## Возможности

- ✅ Реал-тайм обновление данных каждые 0.1 секунды
- ✅ Поддержка Spot и Futures рынков
- ✅ Прямое подключение к Binance WebSocket
- ✅ Динамическое отображение изменений
- ✅ Фильтрация и сортировка символов
- ✅ Мониторинг ликвидаций с уведомлениями
- ✅ Автоматическая очистка старых данных из БД

## Быстрый старт

### 1. Установка и запуск

```bash
# Полная установка и запуск всех сервисов
sudo ./install.sh
```

Скрипт автоматически:
- ✅ Проверит и установит зависимости (Python, Redis, PostgreSQL)
- ✅ Создаст виртуальное окружение
- ✅ Установит все Python пакеты
- ✅ Настроит права доступа
- ✅ Применит миграции БД
- ✅ Соберет статические файлы
- ✅ Создаст systemd сервисы
- ✅ Настроит автоматическую очистку БД
- ✅ Включит автозапуск всех сервисов
- ✅ Запустит все сервисы

### 2. Остановка сервисов

```bash
# Остановка всех сервисов
sudo ./stop.sh
```

### 3. Добавление в автозагрузку

**Автозагрузка уже настроена автоматически при выполнении `install.sh`!**

Все сервисы автоматически добавляются в автозагрузку:
- ✅ `noetdat.service` - основной сервис приложения
- ✅ `redis-server` - сервер Redis
- ✅ `noetdat-cleanup.timer` - автоматическая очистка БД

**Если нужно настроить вручную:**

```bash
# Включить автозапуск основного сервиса
sudo systemctl enable noetdat.service

# Включить автозапуск Redis
sudo systemctl enable redis-server

# Включить автозапуск timer очистки БД
sudo systemctl enable noetdat-cleanup.timer

# Проверить статус автозапуска
systemctl is-enabled noetdat.service
systemctl is-enabled redis-server
systemctl is-enabled noetdat-cleanup.timer
```

### 4. Проверка работы

```bash
# Статус всех сервисов
sudo systemctl status noetdat.service
sudo systemctl status redis-server
sudo systemctl status noetdat-cleanup.timer

# Логи основного сервиса
sudo journalctl -u noetdat.service -f

# Список активных таймеров
sudo systemctl list-timers | grep noetdat
```

## Структура проекта

- `install.sh` - Полная установка и запуск
- `stop.sh` - Остановка всех сервисов
- `requirements.txt` - Список зависимостей Python
- `systemd/` - Systemd unit файлы для автозапуска
- `api/binance_workers.py` - Воркеры для получения данных от Binance
- `api/consumers.py` - WebSocket consumer для отправки данных клиентам
- `static/js/screener.js` - Клиентский код для динамического обновления

## Автоматическая очистка БД

Timer `noetdat-cleanup.timer` автоматически очищает старые данные:
- Запускается каждые 6 часов (00:00, 06:00, 12:00, 18:00)
- При загрузке системы (с задержкой 10 минут)
- Удаляет snapshots старше 2 часов

**Настройка периода хранения:**
```bash
# Отредактировать service файл
sudo nano /etc/systemd/system/noetdat-cleanup.service

# Изменить параметр --hours (например, на 24 для хранения сутки)
ExecStart=... cleanup_old_snapshots --hours 24

# Перезагрузить
sudo systemctl daemon-reload
sudo systemctl restart noetdat-cleanup.timer
```

## Управление сервисами

```bash
# Запуск
sudo systemctl start noetdat.service

# Остановка
sudo systemctl stop noetdat.service

# Перезапуск
sudo systemctl restart noetdat.service

# Статус
sudo systemctl status noetdat.service

# Логи
sudo journalctl -u noetdat.service -f
```

## Требования

- Python 3.10+
- Redis Server
- PostgreSQL (или SQLite для разработки)
- Nginx (для продакшена, опционально)

## Документация

- [AUTOSTART.md](AUTOSTART.md) - Подробная информация об автозапуске и настройке сервисов

## Устранение проблем

### Сервис не запускается

```bash
# Проверить логи
sudo journalctl -u noetdat.service -n 50

# Проверить Redis
sudo systemctl status redis-server
redis-cli ping  # Должен вернуть PONG

# Перезапустить сервис
sudo systemctl restart noetdat.service
```

### Данные не обновляются

```bash
# Проверить подключение к Binance
sudo journalctl -u noetdat.service | grep -i "binance\|websocket"

# Проверить воркеры
sudo journalctl -u noetdat.service | grep -i "worker"
```

### Timer очистки не работает

```bash
# Проверить статус timer
sudo systemctl status noetdat-cleanup.timer

# Проверить последний запуск
sudo journalctl -u noetdat-cleanup.service -n 50

# Запустить вручную для проверки
sudo systemctl start noetdat-cleanup.service
```

## Лицензия

Проект для личного использования.
