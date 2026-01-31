"""
Migration 020: Admin Error Log
Created: 2026-01-27

Таблица для управления ошибками с возможностью:
- Группировки по юзерам
- Апрува ошибок (больше не показываются)
- Отправки напоминаний юзерам
"""


def upgrade(cur):
    """Apply migration - create admin_error_log table"""
    
    # Таблица логов ошибок для админа
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_error_log (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            error_type      TEXT NOT NULL,           -- 'INSUFFICIENT_BALANCE', 'API_ERROR', 'CONNECTION', etc.
            error_code      TEXT,                    -- Код ошибки от биржи (110007, 10001, etc.)
            error_message   TEXT NOT NULL,           -- Полное сообщение ошибки
            context         JSONB DEFAULT '{}',      -- Дополнительный контекст (symbol, side, qty, etc.)
            exchange        TEXT DEFAULT 'bybit',    -- Биржа
            account_type    TEXT DEFAULT 'demo',     -- Тип аккаунта
            
            -- Статусы обработки
            status          TEXT DEFAULT 'new',      -- 'new', 'approved', 'notified', 'resolved'
            approved_at     TIMESTAMP,               -- Когда апрувнули
            notified_at     TIMESTAMP,               -- Когда отправили напоминание юзеру
            admin_note      TEXT,                    -- Заметка админа
            
            -- Счётчики
            occurrence_count INTEGER DEFAULT 1,      -- Сколько раз произошла эта ошибка
            first_seen      TIMESTAMP DEFAULT NOW(), -- Первое появление
            last_seen       TIMESTAMP DEFAULT NOW(), -- Последнее появление
            
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Индексы для быстрого поиска
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_admin_error_log_user_id 
        ON admin_error_log(user_id)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_admin_error_log_status 
        ON admin_error_log(status)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_admin_error_log_error_type 
        ON admin_error_log(error_type)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_admin_error_log_last_seen 
        ON admin_error_log(last_seen DESC)
    """)
    
    # Уникальный индекс для группировки одинаковых ошибок
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_admin_error_log_unique_error 
        ON admin_error_log(user_id, error_type, error_code, exchange, account_type)
        WHERE status != 'approved'
    """)
    
    print("✅ Created admin_error_log table with indexes")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS admin_error_log CASCADE")
    print("✅ Dropped admin_error_log table")
