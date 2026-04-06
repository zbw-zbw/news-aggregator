# -*- coding: utf-8 -*-
"""
One-time migration script to populate the FTS5 table with existing news data.

Run this script once after deploying the FTS5 changes to an existing database:
    python backend/migrate_fts.py

This script will:
1. Create the FTS5 virtual table if it doesn't exist
2. Populate it with all existing news data
"""
import sys
import os
from sqlalchemy import text

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db


def migrate_fts():
    """Populate FTS table with existing news data."""
    with app.app_context():
        print("Starting FTS migration...")
        
        # Check if news_fts table exists
        result = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='news_fts'"
        ))
        if not result.fetchone():
            print("Creating FTS5 virtual table...")
            db.session.execute(text('''
                CREATE VIRTUAL TABLE IF NOT EXISTS news_fts USING fts5(
                    title, summary, content='news', content_rowid='id'
                )
            '''))
            db.session.commit()
            print("FTS5 virtual table created.")
        
        # Clear existing FTS data (in case of re-run)
        print("Clearing existing FTS data...")
        db.session.execute(text("DELETE FROM news_fts"))
        db.session.commit()
        
        # Populate FTS table with existing news data
        print("Populating FTS table with existing news data...")
        result = db.session.execute(text('''
            INSERT INTO news_fts(rowid, title, summary)
            SELECT id, title, summary FROM news
        '''))
        db.session.commit()
        
        # Verify the migration
        count_result = db.session.execute(text("SELECT COUNT(*) FROM news_fts"))
        fts_count = count_result.fetchone()[0]
        
        news_count_result = db.session.execute(text("SELECT COUNT(*) FROM news"))
        news_count = news_count_result.fetchone()[0]
        
        print(f"\nMigration complete!")
        print(f"  News table: {news_count} records")
        print(f"  FTS table:  {fts_count} records")
        
        if fts_count == news_count:
            print("\nSuccess: FTS table fully populated.")
        else:
            print(f"\nWarning: Record count mismatch!")


if __name__ == '__main__':
    migrate_fts()
