"""
Migration 026: Support Chat Tables
===================================
Tables for in-app support chat system.
Users can chat with admin support from iOS/Android/WebApp.
Admin can manage multiple chats simultaneously.
"""


def upgrade(cur):
    """Create support chat tables."""
    
    # Support chat conversations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS support_chats (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'open',        -- open, waiting, resolved, closed
            subject         TEXT,
            language        TEXT DEFAULT 'en',
            created_at      TIMESTAMP DEFAULT NOW(),
            updated_at      TIMESTAMP DEFAULT NOW(),
            resolved_at     TIMESTAMP,
            resolved_by     BIGINT,
            rating          INTEGER,                             -- 1-5 stars
            UNIQUE(user_id, status)                              -- one open chat per user
        )
    """)
    
    # Support chat messages
    cur.execute("""
        CREATE TABLE IF NOT EXISTS support_messages (
            id              SERIAL PRIMARY KEY,
            chat_id         INTEGER NOT NULL REFERENCES support_chats(id) ON DELETE CASCADE,
            sender_id       BIGINT NOT NULL,                     -- user_id or admin_id
            sender_type     TEXT NOT NULL DEFAULT 'user',        -- 'user' or 'admin'
            message         TEXT NOT NULL,
            message_type    TEXT DEFAULT 'text',                 -- text, faq, system, image
            is_read         BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # FAQ answers (pre-made quick responses)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS support_faq (
            id              SERIAL PRIMARY KEY,
            category        TEXT NOT NULL,                       -- 'trading', 'api', 'billing', 'general'
            question        TEXT NOT NULL,
            answer          TEXT NOT NULL,
            language        TEXT DEFAULT 'en',
            sort_order      INTEGER DEFAULT 0,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_support_chats_user ON support_chats(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_support_chats_status ON support_chats(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_support_messages_chat ON support_messages(chat_id, created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_support_faq_lang ON support_faq(language, category)")
    
    # Insert default FAQ entries
    cur.execute("""
        INSERT INTO support_faq (category, question, answer, language, sort_order) VALUES
        ('api', 'How to connect Bybit API?', 'Go to Settings → API Keys → Setup Demo/Real. Enter your API Key and Secret from Bybit. Make sure Read+Trade permissions are enabled.', 'en', 1),
        ('api', 'How to connect HyperLiquid?', 'Go to Settings → API Keys → Setup Testnet/Mainnet. Enter your Private Key. The wallet address is auto-derived.', 'en', 2),
        ('trading', 'Why are my trades not opening?', 'Check: 1) API keys are valid 2) Sufficient balance 3) Strategy is enabled for the correct side (Long/Short) 4) Trading mode matches your setup', 'en', 3),
        ('trading', 'What is DCA?', 'Dollar Cost Averaging adds to your position at lower prices. Configure DCA % triggers in strategy settings.', 'en', 4),
        ('billing', 'How to subscribe?', 'Go to Settings → Premium → Choose plan → Pay with crypto (USDT, BTC, ETH). Your license activates automatically after payment.', 'en', 5),
        ('general', 'How to change language?', 'Go to Settings → Language. 15 languages supported including RTL for Arabic and Hebrew.', 'en', 6),
        ('api', 'Как подключить Bybit API?', 'Настройки → API Ключи → Bybit Demo/Real. Введите API Key и Secret с Bybit. Убедитесь что включены права Read+Trade.', 'ru', 1),
        ('api', 'Как подключить HyperLiquid?', 'Настройки → API Ключи → Testnet/Mainnet. Введите Private Key. Адрес кошелька определится автоматически.', 'ru', 2),
        ('trading', 'Почему не открываются сделки?', 'Проверьте: 1) API ключи валидны 2) Достаточно баланса 3) Стратегия включена для нужной стороны (Long/Short) 4) Режим торговли совпадает', 'ru', 3),
        ('billing', 'Как оплатить подписку?', 'Настройки → Premium → Выбрать план → Оплата криптой (USDT, BTC, ETH). Лицензия активируется автоматически.', 'ru', 5)
        ON CONFLICT DO NOTHING
    """)


def downgrade(cur):
    """Drop support chat tables."""
    cur.execute("DROP TABLE IF EXISTS support_messages CASCADE")
    cur.execute("DROP TABLE IF EXISTS support_faq CASCADE")
    cur.execute("DROP TABLE IF EXISTS support_chats CASCADE")
