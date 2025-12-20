#!/bin/bash
# ============================================
# Скрипт остановки всех сервисов проекта
# ============================================
# НАЗНАЧЕНИЕ: Для СЕРВЕРА (продакшен)
# ============================================
# Использование на сервере: sudo ./stop.sh
# 
# Этот скрипт останавливает все сервисы проекта:
#   - noetdat.service (основной сервис)
#   - noetdat-cleanup.timer (таймер очистки БД)
#   - redis-server (опционально)
# ============================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Переменные
SERVICE_NAME="noetdat.service"

# Функции
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка прав root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        error "Этот скрипт должен быть запущен с правами root (sudo)"
    fi
}

# Остановка основного сервиса
stop_main_service() {
    log "Остановка основного сервиса ($SERVICE_NAME)..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        success "Сервис остановлен"
    else
        warning "Сервис уже остановлен"
    fi
}

# Остановка timer очистки
stop_cleanup_timer() {
    log "Остановка timer очистки БД..."
    
    if systemctl is-active --quiet noetdat-cleanup.timer; then
        systemctl stop noetdat-cleanup.timer
        success "Timer остановлен"
    else
        warning "Timer уже остановлен"
    fi
}

# Остановка Redis (опционально, только если нужно)
stop_redis() {
    log "Остановка Redis..."
    
    read -p "Остановить Redis? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if systemctl is-active --quiet redis-server; then
            systemctl stop redis-server
            success "Redis остановлен"
        else
            warning "Redis уже остановлен"
        fi
    else
        log "Redis не остановлен (может использоваться другими сервисами)"
    fi
}

# Показать статус
show_status() {
    echo ""
    echo -e "${BLUE}=== Текущий статус сервисов ===${NC}"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✓ $SERVICE_NAME: активен${NC}"
    else
        echo -e "${RED}✗ $SERVICE_NAME: остановлен${NC}"
    fi
    
    if systemctl is-active --quiet noetdat-cleanup.timer; then
        echo -e "${GREEN}✓ Timer очистки БД: активен${NC}"
    else
        echo -e "${RED}✗ Timer очистки БД: остановлен${NC}"
    fi
    
    if systemctl is-active --quiet redis-server; then
        echo -e "${GREEN}✓ Redis: активен${NC}"
    else
        echo -e "${RED}✗ Redis: остановлен${NC}"
    fi
    
    echo ""
}

# Главная функция
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  Остановка сервисов проекта"
    echo "=========================================="
    echo -e "${NC}"
    
    check_root
    
    stop_main_service
    stop_cleanup_timer
    stop_redis
    
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  Остановка завершена"
    echo "==========================================${NC}"
    echo ""
    
    show_status
    
    echo -e "${BLUE}Для запуска сервисов используйте:${NC}"
    echo "  sudo systemctl start $SERVICE_NAME"
    echo "  sudo systemctl start noetdat-cleanup.timer"
    echo "  или: sudo ./install.sh"
}

# Запуск
main

