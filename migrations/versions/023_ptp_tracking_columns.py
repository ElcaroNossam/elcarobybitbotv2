"""
Migration: Partial Take Profit Tracking Columns
Version: 023
Created: 2026-02-02

Adds ptp_step_1_done and ptp_step_2_done columns to active_positions table
for tracking Partial Take Profit execution status per position.

This is required for the Partial TP (срез маржи) feature to work correctly
in the monitor_positions_loop.
"""


def upgrade(cur):
    """Apply migration - add PTP tracking columns to active_positions"""
    
    # Check if columns already exist
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'active_positions' AND column_name = 'ptp_step_1_done'
    """)
    if cur.fetchone():
        print("  ⏭️ PTP tracking columns already exist, skipping...")
        return
    
    # Add Partial TP step 1 done column
    cur.execute("""
        ALTER TABLE active_positions 
        ADD COLUMN IF NOT EXISTS ptp_step_1_done INTEGER NOT NULL DEFAULT 0
    """)
    
    # Add Partial TP step 2 done column
    cur.execute("""
        ALTER TABLE active_positions 
        ADD COLUMN IF NOT EXISTS ptp_step_2_done INTEGER NOT NULL DEFAULT 0
    """)
    
    print("  ✅ Added ptp_step_1_done and ptp_step_2_done columns to active_positions")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("ALTER TABLE active_positions DROP COLUMN IF EXISTS ptp_step_1_done")
    cur.execute("ALTER TABLE active_positions DROP COLUMN IF EXISTS ptp_step_2_done")
