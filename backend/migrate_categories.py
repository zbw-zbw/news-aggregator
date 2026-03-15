# -*- coding: utf-8 -*-
"""
Database migration script for category refactoring.
Migrates from old categories to new 6-category system:
- 前端, 后端, 云原生, 人工智能, 区块链, 其他技术

Also creates necessary indexes for performance.

Run this script once after updating the code.
"""
import sqlite3
import os

# Database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'news.db')


def get_existing_indexes(cursor):
    """Get list of existing indexes on the news table."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='news'")
    return [row[0] for row in cursor.fetchall()]


def create_indexes(conn, cursor):
    """Create necessary indexes if they don't exist."""
    print("\n[Step 0] Creating database indexes...")
    
    existing_indexes = get_existing_indexes(cursor)
    
    indexes_to_create = [
        ('idx_news_category', 'CREATE INDEX idx_news_category ON news (category)'),
        ('idx_news_published', 'CREATE INDEX idx_news_published ON news (published)'),
        ('idx_news_hot_score', 'CREATE INDEX idx_news_hot_score ON news (hot_score)'),
        ('idx_category_published', 'CREATE INDEX idx_category_published ON news (category, published)'),
        ('idx_category_hot_score', 'CREATE INDEX idx_category_hot_score ON news (category, hot_score)'),
    ]
    
    created = 0
    for idx_name, idx_sql in indexes_to_create:
        if idx_name not in existing_indexes:
            try:
                cursor.execute(idx_sql)
                print(f"  ✓ Created index: {idx_name}")
                created += 1
            except sqlite3.OperationalError as e:
                print(f"  ⚠ Failed to create index {idx_name}: {e}")
        else:
            print(f"  ✓ Index already exists: {idx_name}")
    
    if created > 0:
        conn.commit()
        print(f"  Created {created} new indexes")


def migrate_database():
    """Run the database migration."""
    print("=" * 50)
    print("Starting category migration...")
    print("=" * 50)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Step 0: Create indexes first (critical for performance)
    create_indexes(conn, cursor)
    
    # Step 1: Check if is_video column exists, add if not
    print("\n[Step 1] Checking is_video column...")
    cursor.execute("PRAGMA table_info(news)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'is_video' not in columns:
        print("  Adding is_video column...")
        cursor.execute("ALTER TABLE news ADD COLUMN is_video BOOLEAN DEFAULT 0")
        conn.commit()
        print("  ✓ is_video column added")
    else:
        print("  ✓ is_video column already exists")
    
    # Step 2: Mark existing YouTube videos
    print("\n[Step 2] Marking existing video content...")
    cursor.execute("""
        UPDATE news 
        SET is_video = 1 
        WHERE category = '技术视频' 
           OR source LIKE '%YouTube%' 
           OR source LIKE '%Fireship%'
           OR source LIKE '%3Blue1Brown%'
           OR source LIKE '%尚硅谷%'
           OR source LIKE '%黑马程序员%'
           OR source LIKE '%Tech With Tim%'
           OR source LIKE '%Computerphile%'
    """)
    video_count = cursor.rowcount
    conn.commit()
    print(f"  ✓ Marked {video_count} items as video content")
    
    # Step 3: Migrate categories
    print("\n[Step 3] Migrating categories...")
    
    # Simple category renames (remove "圈" suffix)
    simple_renames = [
        ('前端圈', '前端'),
        ('后端圈', '后端'),
        ('云原生圈', '云原生'),
        ('区块链圈', '区块链'),
    ]
    
    for old_cat, new_cat in simple_renames:
        cursor.execute("UPDATE news SET category = ? WHERE category = ?", (new_cat, old_cat))
        count = cursor.rowcount
        if count > 0:
            print(f"  ✓ '{old_cat}' → '{new_cat}': {count} items")
    
    # Merge AI-related categories
    ai_categories = ['AI圈', 'AI研究', 'AI+医疗圈']
    for old_cat in ai_categories:
        cursor.execute("UPDATE news SET category = '人工智能' WHERE category = ?", (old_cat,))
        count = cursor.rowcount
        if count > 0:
            print(f"  ✓ '{old_cat}' → '人工智能': {count} items")
    
    # Migrate 技术视频 based on source (already marked as is_video)
    # Fireship -> 前端 (general frontend content)
    cursor.execute("""
        UPDATE news SET category = '前端' 
        WHERE category = '技术视频' AND source LIKE '%Fireship%'
    """)
    count = cursor.rowcount
    if count > 0:
        print(f"  ✓ '技术视频' (Fireship) → '前端': {count} items")
    
    # 3Blue1Brown -> 人工智能 (math/ML visualizations)
    cursor.execute("""
        UPDATE news SET category = '人工智能' 
        WHERE category = '技术视频' AND source LIKE '%3Blue1Brown%'
    """)
    count = cursor.rowcount
    if count > 0:
        print(f"  ✓ '技术视频' (3Blue1Brown) → '人工智能': {count} items")
    
    # Other tech videos -> 其他技术
    cursor.execute("""
        UPDATE news SET category = '其他技术' 
        WHERE category = '技术视频'
    """)
    count = cursor.rowcount
    if count > 0:
        print(f"  ✓ '技术视频' (others) → '其他技术': {count} items")
    
    # Migrate 程序员圈 based on title keywords
    print("\n  Processing '程序员圈' by title keywords...")
    
    # 前端 keywords
    frontend_keywords = ['前端', 'CSS', 'JavaScript', 'JS', 'React', 'Vue', 'Angular', 
                         'Webpack', 'Vite', 'TypeScript', 'TS', 'HTML', 'DOM', '浏览器']
    for keyword in frontend_keywords:
        cursor.execute("""
            UPDATE news SET category = '前端' 
            WHERE category = '程序员圈' AND title LIKE ?
        """, (f'%{keyword}%',))
    
    # 后端 keywords
    backend_keywords = ['后端', 'Java ', 'Java.', 'Go ', 'Go.', 'Golang', '数据库', 
                        '微服务', 'API', 'REST', 'gRPC', '架构', 'Rust', 'Python']
    for keyword in backend_keywords:
        cursor.execute("""
            UPDATE news SET category = '后端' 
            WHERE category = '程序员圈' AND title LIKE ?
        """, (f'%{keyword}%',))
    
    # 云原生 keywords
    cloud_keywords = ['云原生', 'K8s', 'Kubernetes', 'Docker', 'DevOps', '容器', 
                      'Kubernetes', 'Serverless', '微服务']
    for keyword in cloud_keywords:
        cursor.execute("""
            UPDATE news SET category = '云原生' 
            WHERE category = '程序员圈' AND title LIKE ?
        """, (f'%{keyword}%',))
    
    # AI keywords
    ai_keywords = ['AI', '人工智能', '机器学习', '深度学习', 'GPT', 'LLM', 'NLP', 
                   'CV', '神经网络', 'Transformer', 'ChatGPT', 'Claude']
    for keyword in ai_keywords:
        cursor.execute("""
            UPDATE news SET category = '人工智能' 
            WHERE category = '程序员圈' AND title LIKE ?
        """, (f'%{keyword}%',))
    
    # 区块链 keywords
    blockchain_keywords = ['区块链', '比特币', 'Bitcoin', '以太坊', 'Ethereum', 
                          'Web3', 'DeFi', 'NFT', '加密货币', '智能合约']
    for keyword in blockchain_keywords:
        cursor.execute("""
            UPDATE news SET category = '区块链' 
            WHERE category = '程序员圈' AND title LIKE ?
        """, (f'%{keyword}%',))
    
    # Remaining 程序员圈 -> 其他技术
    cursor.execute("""
        UPDATE news SET category = '其他技术' 
        WHERE category = '程序员圈'
    """)
    count = cursor.rowcount
    if count > 0:
        print(f"  ✓ '程序员圈' (remaining) → '其他技术': {count} items")
    
    conn.commit()
    
    # Step 4: Show final category distribution
    print("\n[Step 4] Final category distribution:")
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM news 
        GROUP BY category 
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} items")
    
    # Show video content count
    cursor.execute("SELECT COUNT(*) FROM news WHERE is_video = 1")
    video_total = cursor.fetchone()[0]
    print(f"\n  Video content: {video_total} items")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("Migration completed successfully!")
    print("=" * 50)


if __name__ == '__main__':
    migrate_database()
