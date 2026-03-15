# -*- coding: utf-8 -*-
"""
Script to recategorize all news in the database.
Can be run periodically to fix misclassified articles.
"""
import sqlite3
import sys
from category_classifier import classify_by_title


def recategorize_all_news(db_path='news.db', dry_run=False):
    """
    Recategorize all news in the database based on title keywords.
    
    Args:
        db_path: Path to SQLite database
        dry_run: If True, only print changes without applying them
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all news
    cursor.execute("SELECT id, title, source, category FROM news")
    rows = cursor.fetchall()
    
    print(f"Total news to process: {len(rows)}")
    print("=" * 80)
    
    # Track changes
    changes = {}
    unchanged = 0
    
    for news_id, title, source, current_category in rows:
        # Get new category based on title
        new_category = classify_by_title(title, current_category)
        
        if new_category != current_category:
            key = (current_category, new_category)
            if key not in changes:
                changes[key] = []
            changes[key].append((news_id, title, source))
        else:
            unchanged += 1
    
    # Print summary
    print("\nProposed changes:")
    print("-" * 80)
    total_changes = 0
    for (old_cat, new_cat), items in sorted(changes.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{old_cat} -> {new_cat}: {len(items)} articles")
        total_changes += len(items)
        # Show first 3 examples
        for news_id, title, source in items[:3]:
            print(f"  - {title[:60]}... ({source})")
        if len(items) > 3:
            print(f"  ... and {len(items) - 3} more")
    
    print(f"\n{'=' * 80}")
    print(f"Summary:")
    print(f"  Total articles: {len(rows)}")
    print(f"  Unchanged: {unchanged}")
    print(f"  To be changed: {total_changes}")
    
    if dry_run:
        print("\n[DRY RUN] No changes applied.")
        conn.close()
        return
    
    # Apply changes
    if total_changes > 0:
        confirm = input("\nApply these changes? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Changes cancelled.")
            conn.close()
            return
        
        print("\nApplying changes...")
        for (old_cat, new_cat), items in changes.items():
            news_ids = [item[0] for item in items]
            # Update in batches
            batch_size = 500
            for i in range(0, len(news_ids), batch_size):
                batch = news_ids[i:i + batch_size]
                placeholders = ','.join('?' * len(batch))
                cursor.execute(
                    f"UPDATE news SET category = ? WHERE id IN ({placeholders})",
                    (new_cat, *batch)
                )
        
        conn.commit()
        print(f"Successfully updated {total_changes} articles.")
    else:
        print("\nNo changes needed.")
    
    conn.close()


def recategorize_misc_only(db_path='news.db', dry_run=False):
    """
    Only recategorize news in '其他技术' category.
    Faster and safer for regular maintenance.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get only '其他技术' news
    cursor.execute("SELECT id, title, source, category FROM news WHERE category = '其他技术'")
    rows = cursor.fetchall()
    
    print(f"'其他技术' news to process: {len(rows)}")
    print("=" * 80)
    
    if not rows:
        print("No '其他技术' news to recategorize.")
        conn.close()
        return
    
    # Track changes
    changes = {}
    
    for news_id, title, source, current_category in rows:
        new_category = classify_by_title(title, current_category)
        
        if new_category != current_category:
            if new_category not in changes:
                changes[new_category] = []
            changes[new_category].append((news_id, title, source))
    
    # Print summary
    print("\nProposed changes:")
    print("-" * 80)
    total_changes = 0
    for new_cat, items in sorted(changes.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n其他技术 -> {new_cat}: {len(items)} articles")
        total_changes += len(items)
        for news_id, title, source in items[:3]:
            print(f"  - {title[:60]}... ({source})")
        if len(items) > 3:
            print(f"  ... and {len(items) - 3} more")
    
    print(f"\n{'=' * 80}")
    print(f"Summary:")
    print(f"  Total '其他技术': {len(rows)}")
    print(f"  Will be recategorized: {total_changes}")
    print(f"  Remain '其他技术': {len(rows) - total_changes}")
    
    if dry_run:
        print("\n[DRY RUN] No changes applied.")
        conn.close()
        return
    
    # Apply changes
    if total_changes > 0:
        confirm = input("\nApply these changes? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Changes cancelled.")
            conn.close()
            return
        
        print("\nApplying changes...")
        for new_cat, items in changes.items():
            news_ids = [item[0] for item in items]
            batch_size = 500
            for i in range(0, len(news_ids), batch_size):
                batch = news_ids[i:i + batch_size]
                placeholders = ','.join('?' * len(batch))
                cursor.execute(
                    f"UPDATE news SET category = ? WHERE id IN ({placeholders})",
                    (new_cat, *batch)
                )
        
        conn.commit()
        print(f"Successfully recategorized {total_changes} articles.")
    else:
        print("\nNo changes needed.")
    
    conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Recategorize news articles')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Preview changes without applying them')
    parser.add_argument('--misc-only', action='store_true',
                        help='Only recategorize "其他技术" articles (faster)')
    parser.add_argument('--db', default='news.db',
                        help='Path to database file (default: news.db)')
    
    args = parser.parse_args()
    
    if args.misc_only:
        recategorize_misc_only(args.db, dry_run=args.dry_run)
    else:
        recategorize_all_news(args.db, dry_run=args.dry_run)
