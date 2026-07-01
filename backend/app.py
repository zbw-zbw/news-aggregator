"""
Flask API for the news aggregator.
"""
import sys
import os
import time
import json
import gzip
import logging
from flask import Flask, jsonify, request, g, Response
from flask_cors import CORS
from flask_caching import Cache
from models import db, News
from sqlalchemy import text, or_

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Gzip compression middleware
@app.after_request
def compress_response(response):
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if 'gzip' not in accept_encoding.lower():
        return response
    if response.content_type is None or 'text/' not in response.content_type and 'application/json' not in response.content_type:
        return response
    if response.content_length is not None and response.content_length < 500:
        return response
    response.direct_passthrough = False
    compressed = gzip.compress(response.get_data(), compresslevel=6)
    response.set_data(compressed)
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = str(len(compressed))
    response.headers.pop('Content-Range', None)
    return response

# Cache configuration
# Keep default simple cache for dev; for production with multiple workers, use Redis and set CACHE_TYPE=CACHE_REDIS etc.
cache = Cache(app, config={
    'CACHE_TYPE': os.environ.get('CACHE_TYPE', 'simple'),
    'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300')),
    # if using redis, set CACHE_REDIS_URL env var and set CACHE_TYPE to 'redis'
})

# Database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'news.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLite performance optimizations
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'timeout': 30,
        'check_same_thread': False,
    },
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db.init_app(app)

# NOTE: Removed import-time index creation to avoid blocking during app import/startup.
# Index creation is only done inside init_db() and should be executed once during deployment.


def warmup_db():
    """Warm up database connection and cache indexes."""
    logger.info("Warming up database connection...")
    try:
        # Enable WAL mode for better concurrent read performance
        db.session.execute(text('PRAGMA journal_mode=WAL'))
        db.session.execute(text('PRAGMA synchronous=NORMAL'))
        db.session.execute(text('PRAGMA cache_size=-64000'))  # 64MB cache
        db.session.execute(text('PRAGMA temp_store=MEMORY'))
        
        # Execute simple queries to load indexes into memory
        # This prevents cold-start slowness on first real request
        db.session.execute(text('SELECT COUNT(*) FROM news'))
        db.session.execute(text('SELECT 1 FROM news ORDER BY published DESC LIMIT 1'))
        db.session.commit()
        logger.info("Database warmup complete.")
    except Exception as e:
        logger.warning(f"Database warmup warning: {e}")


# Warm up database on app creation (works for both local and gunicorn)
with app.app_context():
    warmup_db()

@app.before_request
def start_timer():
    """Start request timing."""
    g.start = time.time()

@app.after_request
def log_request(response):
    """Log request details and timing."""
    if hasattr(g, 'start'):
        duration = time.time() - g.start
        logger.info(f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s')
    return response

@app.route('/api/news', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_news():
    """
    Get paginated news list.
    Query params:
        - category: category name from /api/categories (optional)
        - sort: 'newest' or 'hottest' (default: newest)
        - page: page number (default: 1)
        - per_page: items per page (default: 20, max: 100)
        - search: search keyword for title and summary (optional)
    """
    category = request.args.get('category')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()

    per_page = max(1, min(per_page, 100))

    query = News.query
    if category:
        query = query.filter(News.category == category)

    if search:
        # Use LIKE search for simplicity and reliability
        # FTS5 can be enabled later by running migrate_fts.py
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                News.title.like(search_pattern),
                News.summary.like(search_pattern)
            )
        )

    if sort == 'hottest':
        query = query.order_by(News.hot_score.desc())
    else:
        query = query.order_by(News.published.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = [news.to_dict() for news in pagination.items]
    result = json.dumps({
        'items': items,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    }, ensure_ascii=False, separators=(',', ':'))

    return Response(result, mimetype='application/json')

@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    """Get single news item by ID."""
    news = News.query.get_or_404(news_id)
    return jsonify(news.to_dict())

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available categories in predefined order."""
    # Hard-coded to avoid any DB query or computation
    # Note: Intentionally NOT using cache decorator since this is a static array
    # and cache lookup overhead may exceed direct response time
    return jsonify(['AI', '前端', '后端', '云原生', '区块链', '其他'])

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/admin/clear-cache', methods=['POST'])
def clear_cache():
    cache.clear()
    logger.info('Cache cleared')
    return jsonify({'status': 'ok', 'message': 'Cache cleared successfully'})

def init_db():
    """Initialize the database and create indexes."""
    with app.app_context():
        logger.info("Running init_db: creating tables and indexes if not present.")
        db.create_all()
        
        # Enable WAL mode for better performance
        db.session.execute(text('PRAGMA journal_mode=WAL'))
        db.session.execute(text('PRAGMA synchronous=NORMAL'))
        db.session.execute(text('PRAGMA cache_size=-64000'))  # 64MB cache

        # Create indexes for better query performance; doing this inside init_db only.
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_news_category ON news (category)',
            'CREATE INDEX IF NOT EXISTS idx_news_published ON news (published)',
            'CREATE INDEX IF NOT EXISTS idx_news_hot_score ON news (hot_score)',
            'CREATE INDEX IF NOT EXISTS idx_category_published ON news (category, published)',
            'CREATE INDEX IF NOT EXISTS idx_category_hot_score ON news (category, hot_score)',
            # Add index for LIKE search optimization
            'CREATE INDEX IF NOT EXISTS idx_news_title ON news (title)',
            'CREATE INDEX IF NOT EXISTS idx_news_summary ON news (summary)',
        ]
        for idx_sql in indexes:
            try:
                db.session.execute(text(idx_sql))
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")
        
        # Create FTS5 virtual table for full-text search
        fts_sql = '''
            CREATE VIRTUAL TABLE IF NOT EXISTS news_fts USING fts5(
                title, summary, content='news', content_rowid='id'
            )
        '''
        try:
            db.session.execute(text(fts_sql))
            logger.info("FTS5 virtual table created.")
        except Exception as e:
            logger.warning(f"FTS5 table creation warning: {e}")
        
        # Create triggers to keep FTS table in sync with news table
        triggers = [
            '''CREATE TRIGGER IF NOT EXISTS news_ai AFTER INSERT ON news BEGIN
                INSERT INTO news_fts(rowid, title, summary) VALUES (new.id, new.title, new.summary);
            END''',
            '''CREATE TRIGGER IF NOT EXISTS news_ad AFTER DELETE ON news BEGIN
                INSERT INTO news_fts(news_fts, rowid, title, summary) VALUES('delete', old.id, old.title, old.summary);
            END''',
            '''CREATE TRIGGER IF NOT EXISTS news_au AFTER UPDATE ON news BEGIN
                INSERT INTO news_fts(news_fts, rowid, title, summary) VALUES('delete', old.id, old.title, old.summary);
                INSERT INTO news_fts(rowid, title, summary) VALUES (new.id, new.title, new.summary);
            END''',
        ]
        for trigger_sql in triggers:
            try:
                db.session.execute(text(trigger_sql))
            except Exception as e:
                logger.warning(f"Trigger creation warning: {e}")
        
        db.session.commit()
        logger.info("init_db completed.")

if __name__ == '__main__':
    # Support a one-off init command: `python backend/app.py --init-db`
    if '--init-db' in sys.argv:
        init_db()
        print("Database initialized (init_db).")
        sys.exit(0)

    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
