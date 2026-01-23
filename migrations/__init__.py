"""
Database Migration System for Lyxen Trading Platform
======================================================

This module provides a clean, versioned migration system for PostgreSQL.

Usage:
    python -m migrations.runner upgrade    # Apply all pending migrations
    python -m migrations.runner downgrade  # Rollback last migration
    python -m migrations.runner status     # Show migration status
    python -m migrations.runner reset      # Reset database (DANGEROUS!)
"""
