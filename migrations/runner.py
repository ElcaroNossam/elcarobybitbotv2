"""
Migration Runner - Execute database migrations in order
"""
import os
import sys
import importlib
import logging
from datetime import datetime
from typing import List, Tuple, Optional

import psycopg2
import psycopg2.extras

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro"
)


def get_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)


def ensure_migrations_table():
    """Create migrations tracking table if not exists"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT NOW(),
                    checksum VARCHAR(64)
                )
            """)
            conn.commit()
    logger.info("✅ Migrations table ready")


def get_applied_migrations() -> List[str]:
    """Get list of applied migration versions"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version FROM _migrations ORDER BY version")
            return [row[0] for row in cur.fetchall()]


def get_available_migrations() -> List[Tuple[str, str]]:
    """Get list of available migrations from versions/ folder"""
    migrations_dir = os.path.join(os.path.dirname(__file__), 'versions')
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
        return []
    
    migrations = []
    for filename in sorted(os.listdir(migrations_dir)):
        if filename.endswith('.py') and not filename.startswith('_'):
            version = filename.split('_')[0]
            name = filename[:-3]  # Remove .py
            migrations.append((version, name))
    
    return migrations


def apply_migration(version: str, name: str):
    """Apply a single migration"""
    logger.info(f"📦 Applying migration: {name}")
    
    module_name = f"migrations.versions.{name}"
    module = importlib.import_module(module_name)
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                # Run upgrade
                module.upgrade(cur)
                
                # Record migration
                cur.execute(
                    "INSERT INTO _migrations (version, name) VALUES (%s, %s)",
                    (version, name)
                )
                conn.commit()
                logger.info(f"✅ Applied: {name}")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Failed: {name} - {e}")
                raise


def rollback_migration(version: str, name: str):
    """Rollback a single migration"""
    logger.info(f"⏪ Rolling back: {name}")
    
    module_name = f"migrations.versions.{name}"
    module = importlib.import_module(module_name)
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                # Run downgrade
                if hasattr(module, 'downgrade'):
                    module.downgrade(cur)
                
                # Remove migration record
                cur.execute("DELETE FROM _migrations WHERE version = %s", (version,))
                conn.commit()
                logger.info(f"✅ Rolled back: {name}")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Rollback failed: {name} - {e}")
                raise


def upgrade():
    """Apply all pending migrations"""
    ensure_migrations_table()
    
    applied = set(get_applied_migrations())
    available = get_available_migrations()
    
    pending = [(v, n) for v, n in available if v not in applied]
    
    if not pending:
        logger.info("✅ Database is up to date")
        return
    
    logger.info(f"📋 {len(pending)} migration(s) to apply")
    
    for version, name in pending:
        apply_migration(version, name)
    
    # Invalidate schema cache after migrations
    try:
        from db import invalidate_schema_cache
        invalidate_schema_cache()
        logger.info("✅ Schema cache invalidated")
    except Exception as e:
        logger.warning(f"Could not invalidate schema cache: {e}")
    
    logger.info(f"✅ Applied {len(pending)} migration(s)")


def downgrade(steps: int = 1):
    """Rollback migrations"""
    ensure_migrations_table()
    
    applied = get_applied_migrations()
    
    if not applied:
        logger.info("No migrations to rollback")
        return
    
    # Get migration details
    available = {v: n for v, n in get_available_migrations()}
    
    to_rollback = applied[-steps:]
    to_rollback.reverse()  # Rollback in reverse order
    
    for version in to_rollback:
        name = available.get(version)
        if name:
            rollback_migration(version, name)


def status():
    """Show migration status"""
    ensure_migrations_table()
    
    applied = set(get_applied_migrations())
    available = get_available_migrations()
    
    print("\n📊 Migration Status:")
    print("=" * 60)
    
    for version, name in available:
        status = "✅ Applied" if version in applied else "⏳ Pending"
        print(f"  {version} | {name:<40} | {status}")
    
    pending = len([v for v, n in available if v not in applied])
    print("=" * 60)
    print(f"  Total: {len(available)} | Applied: {len(applied)} | Pending: {pending}\n")


def reset():
    """Reset database - DROP ALL TABLES (DANGEROUS!)"""
    confirm = input("⚠️  This will DROP ALL TABLES! Type 'yes' to confirm: ")
    if confirm != 'yes':
        print("Aborted.")
        return
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Get all tables
            cur.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            # Drop all tables
            for table in tables:
                cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                logger.info(f"Dropped: {table}")
            
            conn.commit()
    
    logger.info("✅ Database reset complete")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python -m migrations.runner [upgrade|downgrade|status|reset]")
        return
    
    command = sys.argv[1]
    
    if command == 'upgrade':
        upgrade()
    elif command == 'downgrade':
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        downgrade(steps)
    elif command == 'status':
        status()
    elif command == 'reset':
        reset()
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
