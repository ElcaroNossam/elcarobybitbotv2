#!/bin/bash
# ============================================
# Полный скрипт установки и запуска проекта
# ============================================
# НАЗНАЧЕНИЕ: Для СЕРВЕРА (продакшен)
# ============================================
# Использование на сервере: sudo ./install.sh
# 
# Этот скрипт предназначен для использования на СЕРВЕРЕ.
# Он выполняет полную установку и настройку проекта:
#   - Установка зависимостей (Python, Redis, PostgreSQL)
#   - Создание виртуального окружения
#   - Установка Python пакетов
#   - Настройка прав доступа
#   - Применение миграций БД
#   - Сбор статических файлов
#   - Настройка systemd сервисов
#   - Автозапуск сервисов
# ============================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Переменные
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="noetdat.service"
SYSTEMD_DIR="/etc/systemd/system"
LOG_FILE="$PROJECT_DIR/logs/install.log"
# Определяем реального пользователя (если запущено с sudo, берем SUDO_USER)
CURRENT_USER="${SUDO_USER:-$(whoami)}"
if [ "$CURRENT_USER" = "root" ] && [ -n "$SUDO_USER" ]; then
    CURRENT_USER="$SUDO_USER"
fi

# Проверяем и логируем пути
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log "============================================"
log "Проверка путей виртуального окружения:"
log "PROJECT_DIR: $PROJECT_DIR"
log "VENV_DIR: $VENV_DIR"
log "PYTHON: $VENV_DIR/bin/python"
log "PIP: $VENV_DIR/bin/pip"
log "DAPHNE: $VENV_DIR/bin/daphne"
log "CURRENT_USER: $CURRENT_USER"
log "============================================"

# Создаем директорию для логов
mkdir -p "$PROJECT_DIR/logs"

# Функции логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

# Логируем начальные пути для проверки
log "============================================"
log "Проверка путей виртуального окружения:"
log "PROJECT_DIR: $PROJECT_DIR"
log "VENV_DIR: $VENV_DIR"
log "PYTHON: $VENV_DIR/bin/python"
log "PIP: $VENV_DIR/bin/pip"
log "DAPHNE: $VENV_DIR/bin/daphne"
log "CURRENT_USER: $CURRENT_USER"
log "============================================"

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Проверка прав root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        error "Этот скрипт должен быть запущен с правами root (sudo)"
    fi
}

# Проверка Python
check_python() {
    log "Проверка Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
            success "Python $PYTHON_VERSION установлен"
        else
            error "Требуется Python 3.10+, установлен $PYTHON_VERSION"
        fi
    else
        error "Python3 не установлен. Установите: sudo apt-get install python3 python3-venv python3-pip"
    fi
}

# Создание виртуального окружения
setup_venv() {
    log "Настройка виртуального окружения..."
    log "VENV_DIR: $VENV_DIR"
    
    if [ ! -d "$VENV_DIR" ]; then
        # Создаем venv от имени правильного пользователя
        log "Создание виртуального окружения в $VENV_DIR..."
        sudo -u "$CURRENT_USER" python3 -m venv "$VENV_DIR" || python3 -m venv "$VENV_DIR"
        success "Виртуальное окружение создано"
    else
        success "Виртуальное окружение уже существует"
    fi
    
    # Проверяем наличие python и pip в venv
    if [ ! -f "$VENV_DIR/bin/python" ]; then
        error "Python не найден в $VENV_DIR/bin/python"
    else
        log "✓ Python найден: $VENV_DIR/bin/python"
        "$VENV_DIR/bin/python" --version 2>&1 | tee -a "$LOG_FILE" || true
    fi
    
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        error "pip не найден в $VENV_DIR/bin/pip"
    else
        log "✓ pip найден: $VENV_DIR/bin/pip"
    fi
    
    # Исправляем права на исполняемые файлы в venv
    log "Исправление прав доступа в виртуальном окружении..."
    chmod +x "$VENV_DIR/bin/"* 2>/dev/null || true
    chown -R "$CURRENT_USER:$CURRENT_USER" "$VENV_DIR" 2>/dev/null || true
    success "Права в виртуальном окружении исправлены"
}

# Установка зависимостей
install_dependencies() {
    log "Установка зависимостей Python..."
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        error "Файл requirements.txt не найден"
    fi
    
    # Исправляем права на весь venv перед использованием
    log "Исправление прав доступа в venv..."
    chmod -R u+x "$VENV_DIR/bin/" 2>/dev/null || true
    chown -R "$CURRENT_USER:$CURRENT_USER" "$VENV_DIR" 2>/dev/null || true
    
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        error "pip не найден в виртуальном окружении. Пересоздайте venv."
    fi
    
    # Используем sudo -u для запуска от имени правильного пользователя
    log "Обновление pip..."
    if sudo -u "$CURRENT_USER" "$VENV_DIR/bin/pip" install --upgrade pip 2>/dev/null; then
        success "pip обновлен"
    else
        # Если sudo -u не работает, пробуем напрямую (но сначала исправляем права)
        chmod +x "$VENV_DIR/bin/pip" 2>/dev/null || true
        "$VENV_DIR/bin/pip" install --upgrade pip || error "Не удалось обновить pip"
    fi
    
    log "Установка зависимостей из requirements.txt..."
    if sudo -u "$CURRENT_USER" "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt" 2>/dev/null; then
        success "Зависимости установлены"
    else
        # Если sudo -u не работает, пробуем напрямую
        "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt" || error "Не удалось установить зависимости"
        success "Зависимости установлены"
    fi
    
    # Проверяем, что daphne установлен
    if [ ! -f "$VENV_DIR/bin/daphne" ]; then
        log "daphne не найден, устанавливаю..."
        if sudo -u "$CURRENT_USER" "$VENV_DIR/bin/pip" install daphne 2>/dev/null; then
            success "daphne установлен"
        else
            "$VENV_DIR/bin/pip" install daphne || error "Не удалось установить daphne"
            success "daphne установлен"
        fi
        chmod +x "$VENV_DIR/bin/daphne" 2>/dev/null || true
    else
        success "daphne уже установлен"
    fi
}

# Установка и настройка Redis
setup_redis() {
    log "Настройка Redis..."
    
    if ! command -v redis-server &> /dev/null; then
        warning "Redis не установлен. Устанавливаю..."
        apt-get update
        apt-get install -y redis-server
        success "Redis установлен"
    else
        success "Redis уже установлен"
    fi
    
    # Включаем автозапуск
    systemctl enable redis-server
    systemctl start redis-server
    
    # Проверяем работу
    if redis-cli ping &> /dev/null; then
        success "Redis запущен и работает"
    else
        error "Redis не отвечает"
    fi
}

# Установка и настройка PostgreSQL (опционально)
setup_postgresql() {
    log "Проверка PostgreSQL..."
    
    if systemctl list-unit-files | grep -q postgresql.service; then
        systemctl enable postgresql
        systemctl start postgresql
        success "PostgreSQL настроен"
    else
        warning "PostgreSQL не установлен (используется SQLite)"
    fi
}

# Настройка прав доступа
setup_permissions() {
    log "Настройка прав доступа..."
    
    # Устанавливаем владельца для всех файлов проекта
    chown -R "$CURRENT_USER:$CURRENT_USER" "$PROJECT_DIR"
    
    # Даем полные права на весь проект (чтение, запись, выполнение)
    chmod -R 755 "$PROJECT_DIR"
    
    # Права на выполнение для скриптов
    chmod +x "$PROJECT_DIR/manage.py" 2>/dev/null || true
    chmod +x "$PROJECT_DIR/install.sh"
    chmod +x "$PROJECT_DIR/stop.sh"
    
    # Права на все Python файлы (для выполнения)
    find "$PROJECT_DIR" -name "*.py" -type f -exec chmod 755 {} \; 2>/dev/null || true
    
    # Права на все shell скрипты
    find "$PROJECT_DIR" -name "*.sh" -type f -exec chmod 755 {} \; 2>/dev/null || true
    
    # Права на директории (полный доступ)
    find "$PROJECT_DIR" -type d -exec chmod 755 {} \; 2>/dev/null || true
    
    # Права на файлы (чтение и запись)
    find "$PROJECT_DIR" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Затем снова даем права на выполнение для скриптов
    find "$PROJECT_DIR" -name "*.sh" -type f -exec chmod 755 {} \; 2>/dev/null || true
    find "$PROJECT_DIR" -name "*.py" -type f -exec chmod 755 {} \; 2>/dev/null || true
    chmod +x "$PROJECT_DIR/manage.py" 2>/dev/null || true
    
    success "Права доступа настроены (полные права на проект)"
}

# Применение миграций
apply_migrations() {
    log "Применение миграций базы данных..."
    
    # Используем прямой путь к python из venv (работает с sudo)
    log "Используется Python: $VENV_DIR/bin/python"
    "$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" makemigrations --noinput
    "$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" migrate --noinput
    
    success "Миграции применены"
}

# Сбор статических файлов
collect_static() {
    log "Сбор статических файлов..."
    
    # Используем прямой путь к python из venv (работает с sudo)
    log "Используется Python: $VENV_DIR/bin/python"
    "$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" collectstatic --noinput --clear
    
    success "Статические файлы собраны"
}

# Очистка старых данных
cleanup_old_data() {
    log "Очистка старых данных из БД..."
    
    # Используем прямой путь к python из venv (работает с sudo)
    log "Используется Python: $VENV_DIR/bin/python"
    "$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" cleanup_old_snapshots --hours 2 || warning "Очистка данных пропущена (возможно, БД пуста)"
    
    success "Очистка данных завершена"
}

# Создание systemd service файла
create_service_file() {
    log "Создание systemd service файла..."
    
    SERVICE_FILE="$SYSTEMD_DIR/$SERVICE_NAME"
    
    if [ -f "$SERVICE_FILE" ]; then
        warning "Service файл уже существует, обновляю..."
    fi
    
    # Проверяем наличие daphne перед созданием service файла
    log "Проверка daphne: $VENV_DIR/bin/daphne"
    if [ ! -f "$VENV_DIR/bin/daphne" ]; then
        error "daphne не найден в $VENV_DIR/bin/daphne. Установите: $VENV_DIR/bin/pip install daphne"
    else
        log "✓ daphne найден: $VENV_DIR/bin/daphne"
    fi
    
    # Исправляем права на daphne
    chmod +x "$VENV_DIR/bin/daphne" 2>/dev/null || true
    chown "$CURRENT_USER:$CURRENT_USER" "$VENV_DIR/bin/daphne" 2>/dev/null || true
    
    # Проверяем, что daphne исполняемый
    if [ ! -x "$VENV_DIR/bin/daphne" ]; then
        error "daphne не имеет прав на выполнение: $VENV_DIR/bin/daphne"
    fi
    
    log "Финальные пути для service файла:"
    log "  ExecStart: $VENV_DIR/bin/daphne"
    log "  WorkingDirectory: $PROJECT_DIR"
    log "  User: $CURRENT_USER"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Noet-Dat ASGI daemon (WebSocket support)
After=network.target redis-server.service postgresql.service
Requires=redis-server.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings"
ExecStart=$VENV_DIR/bin/daphne -b 127.0.0.1 -p 8000 --access-log $PROJECT_DIR/logs/daphne_access.log --proxy-headers config.asgi:application
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=noetdat

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    success "Service файл создан: $SERVICE_FILE"
}

# Настройка timer очистки БД
setup_cleanup_timer() {
    log "Настройка автоматической очистки БД..."
    
    # Копируем service файл
    if [ -f "$PROJECT_DIR/systemd/noetdat-cleanup.service" ]; then
        cp "$PROJECT_DIR/systemd/noetdat-cleanup.service" "$SYSTEMD_DIR/"
        
        # Обновляем пути
        sed -i "s|/home/ubuntu/project/noetdat|$PROJECT_DIR|g" "$SYSTEMD_DIR/noetdat-cleanup.service"
        sed -i "s|User=ubuntu|User=$CURRENT_USER|g" "$SYSTEMD_DIR/noetdat-cleanup.service"
        sed -i "s|Group=ubuntu|Group=$CURRENT_USER|g" "$SYSTEMD_DIR/noetdat-cleanup.service"
        
        success "Service файл очистки обновлен"
    else
        warning "Service файл очистки не найден, создаю..."
        
        cat > "$SYSTEMD_DIR/noetdat-cleanup.service" << EOF
[Unit]
Description=Noet-Dat Database Cleanup Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=oneshot
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/manage.py cleanup_old_snapshots --hours 2
StandardOutput=journal
StandardError=journal
SyslogIdentifier=noetdat-cleanup
EOF
    fi
    
    # Копируем timer файл
    if [ -f "$PROJECT_DIR/systemd/noetdat-cleanup.timer" ]; then
        cp "$PROJECT_DIR/systemd/noetdat-cleanup.timer" "$SYSTEMD_DIR/"
    else
        warning "Timer файл не найден, создаю..."
        
        cat > "$SYSTEMD_DIR/noetdat-cleanup.timer" << EOF
[Unit]
Description=Noet-Dat Database Cleanup Timer
Requires=noetdat-cleanup.service

[Timer]
OnCalendar=*-*-* 00,06,12,18:00:00
OnBootSec=10min
Persistent=true
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF
    fi
    
    systemctl daemon-reload
    systemctl enable noetdat-cleanup.timer
    systemctl start noetdat-cleanup.timer
    
    success "Timer очистки БД настроен и запущен"
}

# Включение автозапуска
enable_autostart() {
    log "Включение автозапуска сервисов..."
    
    # Redis
    systemctl enable redis-server
    success "Автозапуск Redis включен"
    
    # PostgreSQL (если установлен)
    if systemctl list-unit-files | grep -q postgresql.service; then
        systemctl enable postgresql
        success "Автозапуск PostgreSQL включен"
    fi
    
    # Основной сервис
    systemctl enable "$SERVICE_NAME"
    success "Автозапуск основного сервиса включен"
    
    # Timer очистки
    systemctl enable noetdat-cleanup.timer
    success "Автозапуск timer очистки включен"
}

# Запуск сервисов
start_services() {
    log "Запуск сервисов..."
    
    # Redis
    systemctl start redis-server
    success "Redis запущен"
    
    # PostgreSQL (если установлен)
    if systemctl list-unit-files | grep -q postgresql.service; then
        systemctl start postgresql
        success "PostgreSQL запущен"
    fi
    
    # Основной сервис
    systemctl start "$SERVICE_NAME"
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Основной сервис запущен"
    else
        error "Не удалось запустить основной сервис. Проверьте логи: sudo journalctl -u $SERVICE_NAME -n 50"
    fi
}

# Проверка статуса
check_status() {
    log "Проверка статуса сервисов..."
    
    echo ""
    echo -e "${BLUE}=== Статус сервисов ===${NC}"
    
    # Redis
    if systemctl is-active --quiet redis-server; then
        echo -e "${GREEN}✓ Redis: активен${NC}"
    else
        echo -e "${RED}✗ Redis: не активен${NC}"
    fi
    
    # Основной сервис
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✓ $SERVICE_NAME: активен${NC}"
    else
        echo -e "${RED}✗ $SERVICE_NAME: не активен${NC}"
    fi
    
    # Timer очистки
    if systemctl is-enabled --quiet noetdat-cleanup.timer; then
        echo -e "${GREEN}✓ Timer очистки БД: включен${NC}"
        NEXT_RUN=$(systemctl list-timers --no-pager 2>/dev/null | grep "noetdat-cleanup" | awk '{print $1, $2, $3, $4, $5}' | head -1 || echo "N/A")
        if [ "$NEXT_RUN" != "N/A" ]; then
            echo -e "${BLUE}  Следующий запуск: $NEXT_RUN${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Timer очистки БД: не включен${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Проверка автозапуска:${NC}"
    systemctl is-enabled redis-server && echo -e "${GREEN}✓ Redis: автозапуск включен${NC}" || echo -e "${RED}✗ Redis: автозапуск не включен${NC}"
    systemctl is-enabled "$SERVICE_NAME" && echo -e "${GREEN}✓ $SERVICE_NAME: автозапуск включен${NC}" || echo -e "${RED}✗ $SERVICE_NAME: автозапуск не включен${NC}"
    systemctl is-enabled noetdat-cleanup.timer && echo -e "${GREEN}✓ Timer очистки: автозапуск включен${NC}" || echo -e "${RED}✗ Timer очистки: автозапуск не включен${NC}"
    
    echo ""
    echo -e "${BLUE}Полезные команды:${NC}"
    echo "  sudo systemctl status $SERVICE_NAME"
    echo "  sudo journalctl -u $SERVICE_NAME -f"
    echo "  sudo systemctl restart $SERVICE_NAME"
    echo "  ./stop.sh  # Остановка всех сервисов"
}

# Главная функция
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  Установка и запуск проекта"
    echo "=========================================="
    echo -e "${NC}"
    
    check_root
    check_python
    setup_venv
    install_dependencies
    setup_redis
    setup_postgresql
    setup_permissions
    apply_migrations
    collect_static
    cleanup_old_data
    create_service_file
    setup_cleanup_timer
    enable_autostart
    start_services
    
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  Установка завершена успешно!"
    echo "==========================================${NC}"
    echo ""
    
    check_status
}

# Запуск
main

