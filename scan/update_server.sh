#!/bin/bash
# ============================================
# Скрипт для обновления кода на СЕРВЕРЕ
# ============================================
# НАЗНАЧЕНИЕ: Для СЕРВЕРА (продакшен)
# ============================================
# Использование на сервере:
#   1. Скопировать на сервер (с локальной машины):
#      scp update_server.sh ubuntu@ваш_сервер_ip:/home/ubuntu/project/noetdat/
#   
#   2. На сервере (через SSH):
#      ssh ubuntu@ваш_сервер_ip
#      cd /home/ubuntu/project/noetdat
#      chmod +x update_server.sh
#      ./update_server.sh
# 
# Скрипт автоматически:
#   - Проверит локальные изменения на сервере
#   - Закоммитит их перед pull
#   - Обновит код с GitHub
#   - Предложит перезапустить сервис
# ============================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Автоматически определяем директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

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

# Проверка директории
if [ ! -d "$PROJECT_DIR" ]; then
    error "Директория проекта не найдена: $PROJECT_DIR"
fi

cd "$PROJECT_DIR" || error "Не удалось перейти в директорию проекта"

log "Проверка статуса Git..."

# Проверка изменений
if ! git diff-index --quiet HEAD --; then
    warning "Найдены локальные изменения на сервере"
    
    # Показать измененные файлы
    echo -e "\n${YELLOW}Измененные файлы:${NC}"
    git diff --name-only
    
    # Показать краткую информацию об изменениях
    echo -e "\n${YELLOW}Краткая информация об изменениях:${NC}"
    git diff --stat
    
    # Автоматически коммитим изменения на сервере
    log "Автоматическое коммитирование изменений на сервере..."
    
    # Добавить все изменения
    git add . || error "Ошибка при добавлении файлов"
    
    # Создать коммит с информацией о сервере
    SERVER_HOSTNAME=$(hostname)
    COMMIT_MSG="Server auto-commit before pull: $(date +'%Y-%m-%d %H:%M:%S') on $SERVER_HOSTNAME"
    git commit -m "$COMMIT_MSG" || error "Ошибка при создании коммита"
    
    success "Изменения закоммичены на сервере"
    warning "Внимание: Коммит создан только локально на сервере!"
    warning "Для отправки на GitHub выполните: git push origin main"
else
    success "Локальных изменений нет"
fi

# Выполнить pull
log "Обновление кода с GitHub..."
if git pull --no-edit; then
    success "Код успешно обновлен!"
    
    # Применение миграций БД
    log "Проверка миграций БД..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        if python manage.py migrate --check &>/dev/null; then
            success "Миграции не требуются"
        else
            log "Применение миграций..."
            if python manage.py migrate; then
                success "Миграции применены"
            else
                warning "Ошибка при применении миграций"
            fi
        fi
        
        # Сборка статики
        log "Сборка статических файлов..."
        if python manage.py collectstatic --noinput --clear; then
            success "Статика собрана в staticfiles/"
        else
            warning "Ошибка при сборке статики"
        fi
    else
        warning "Виртуальное окружение не найдено, пропускаем миграции и статику"
    fi
    
    # Опционально: перезапустить сервис
    if systemctl is-active --quiet noetdat.service 2>/dev/null; then
        read -p "$(echo -e ${YELLOW}Перезапустить сервис noetdat.service? [y/N]: ${NC})" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Перезапуск сервиса..."
            if sudo systemctl restart noetdat.service; then
                success "Сервис перезапущен"
                log "Проверка статуса сервиса..."
                sleep 2
                if systemctl is-active --quiet noetdat.service; then
                    success "Сервис успешно запущен"
                else
                    error "Сервис не запустился. Проверьте логи: sudo journalctl -u noetdat.service -n 50"
                fi
            else
                error "Не удалось перезапустить сервис (возможно, нет прав sudo)"
            fi
        fi
    else
        warning "Сервис noetdat.service не запущен"
        read -p "$(echo -e ${YELLOW}Запустить сервис? [y/N]: ${NC})" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Запуск сервиса..."
            if sudo systemctl start noetdat.service; then
                success "Сервис запущен"
            else
                error "Не удалось запустить сервис"
            fi
        fi
    fi
else
    error "Ошибка при обновлении кода. Возможны конфликты."
    echo -e "\n${YELLOW}Для разрешения конфликтов:${NC}"
    echo "1. Отредактируйте файлы с конфликтами"
    echo "2. Выполните: git add ."
    echo "3. Выполните: git commit -m 'Merge: разрешение конфликтов'"
    exit 1
fi

echo -e "\n${GREEN}=== Готово! ===${NC}\n"

