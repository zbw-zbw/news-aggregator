# -*- coding: utf-8 -*-
"""
Migration script to add source_type column to existing database.
"""
import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'news.db')


def migrate():
    """Add source_type column to news table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(news)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'source_type' in columns:
            print("Column 'source_type' already exists. Skipping migration.")
            conn.close()
            return

        # Add the source_type column
        cursor.execute("ALTER TABLE news ADD COLUMN source_type VARCHAR(20) DEFAULT 'rss'")
        conn.commit()
        print("Successfully added 'source_type' column to news table.")

        # Update existing records based on source patterns
        cursor.execute("UPDATE news SET source_type = 'youtube' WHERE is_video = 1")
        cursor.execute("UPDATE news SET source_type = 'arxiv' WHERE source LIKE '%arXiv%'")
        conn.commit()

        # Show summary
        cursor.execute("SELECT source_type, COUNT(*) FROM news GROUP BY source_type")
        results = cursor.fetchall()
        print("\nSource type distribution:")
        for source_type, count in results:
            print(f"  {source_type}: {count}")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    migrate()
