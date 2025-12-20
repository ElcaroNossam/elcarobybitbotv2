#!/usr/bin/env python
"""
Worker Monitor Service
Отслеживает состояние WebSocket воркеров и перезапускает их при необходимости
"""
import os
import sys
import django
import subprocess
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from screener.models import ScreenerSnapshot
from django.utils import timezone

# Настройки
CHECK_INTERVAL = 600  # Проверка каждые 60 секунд
MAX_NO_UPDATE_TIME = 1800  # Перезапуск если нет обновлений 3 минуты
SERVICE_NAME = "ws-workers.service"
LOG_FILE = "/home/ubuntu/project/noetdat/logs/monitor_workers.log"


def log(message):
    """Логирование с timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # Запись в файл
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_message + '\n')
    except Exception as e:
        print(f"Failed to write to log file: {e}")


def get_last_snapshot_time():
    """Получить время последнего снапшота"""
    try:
        latest = ScreenerSnapshot.objects.order_by('-ts').first()
        if latest:
            return latest.ts
        return None
    except Exception as e:
        log(f"ERROR: Failed to get last snapshot: {e}")
        return None


def restart_workers():
    """Перезапустить воркеры через systemd"""
    try:
        log(f"Restarting {SERVICE_NAME}...")
        
        # Перезапуск через systemctl --user
        result = subprocess.run(
            ['systemctl', '--user', 'restart', SERVICE_NAME],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log(f"✅ {SERVICE_NAME} restarted successfully")
            return True
        else:
            log(f"❌ Failed to restart {SERVICE_NAME}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log(f"❌ Timeout while restarting {SERVICE_NAME}")
        return False
    except Exception as e:
        log(f"❌ Error restarting {SERVICE_NAME}: {e}")
        return False


def check_workers_status():
    """Проверить статус воркеров через systemd"""
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'is-active', SERVICE_NAME],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        status = result.stdout.strip()
        return status == 'active'
        
    except Exception as e:
        log(f"ERROR: Failed to check service status: {e}")
        return False


def main():
    """Основной цикл мониторинга"""
    log("=" * 70)
    log("Worker Monitor Service started")
    log(f"Check interval: {CHECK_INTERVAL}s")
    log(f"Max no-update time: {MAX_NO_UPDATE_TIME}s")
    log("=" * 70)
    
    last_restart_time = None
    restart_cooldown = 300  # 5 минут между перезапусками
    
    while True:
        try:
            # Проверка статуса сервиса
            is_active = check_workers_status()
            
            if not is_active:
                log(f"⚠️ {SERVICE_NAME} is not active!")
                
                # Проверка cooldown
                if last_restart_time:
                    time_since_restart = (datetime.now() - last_restart_time).total_seconds()
                    if time_since_restart < restart_cooldown:
                        log(f"⏳ Cooldown active, waiting {int(restart_cooldown - time_since_restart)}s")
                        time.sleep(CHECK_INTERVAL)
                        continue
                
                # Перезапуск
                if restart_workers():
                    last_restart_time = datetime.now()
                    time.sleep(30)  # Ждём 30 секунд после перезапуска
                    continue
            
            # Проверка времени последнего обновления
            last_snapshot_time = get_last_snapshot_time()
            
            if last_snapshot_time:
                # Убираем timezone для сравнения
                if timezone.is_aware(last_snapshot_time):
                    last_snapshot_time = timezone.make_naive(last_snapshot_time)
                
                time_diff = (datetime.now() - last_snapshot_time).total_seconds()
                
                log(f"Last snapshot: {last_snapshot_time.strftime('%H:%M:%S')} ({int(time_diff)}s ago)")
                
                if time_diff > MAX_NO_UPDATE_TIME:
                    log(f"⚠️ No updates for {int(time_diff)}s (max: {MAX_NO_UPDATE_TIME}s)")
                    
                    # Проверка cooldown
                    if last_restart_time:
                        time_since_restart = (datetime.now() - last_restart_time).total_seconds()
                        if time_since_restart < restart_cooldown:
                            log(f"⏳ Cooldown active, waiting {int(restart_cooldown - time_since_restart)}s")
                            time.sleep(CHECK_INTERVAL)
                            continue
                    
                    # Перезапуск
                    if restart_workers():
                        last_restart_time = datetime.now()
                        time.sleep(30)  # Ждём 30 секунд после перезапуска
                        continue
                else:
                    log(f"✅ Workers are healthy")
            else:
                log("⚠️ No snapshots found in database")
            
            # Ждём до следующей проверки
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("Monitor service stopped by user")
            break
        except Exception as e:
            log(f"ERROR: Unexpected error in main loop: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
