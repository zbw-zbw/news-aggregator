"""
Flask API for the news aggregator.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, News
import os

app = Flask(__name__)
CORS(app)

# Database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'news.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# Create indexes on app startup
with app.app_context():
    from sqlalchemy import text
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_news_category ON news (category)',
        'CREATE INDEX IF NOT EXISTS idx_news_published ON news (published)',
        'CREATE INDEX IF NOT EXISTS idx_news_hot_score ON news (hot_score)',
        'CREATE INDEX IF NOT EXISTS idx_category_published ON news (category, published)',
        'CREATE INDEX IF NOT EXISTS idx_category_hot_score ON news (category, hot_score)',
    ]
    for idx_sql in indexes:
        try:
            db.session.execute(text(idx_sql))
        except Exception:
            pass
    db.session.commit()


@app.route('/api/news', methods=['GET'])
def get_news():
    """
    Get paginated news list.
    Query params:
        - category: category name from /api/categories (optional)
        - sort: 'newest' or 'hottest' (default: newest)
        - page: page number (default: 1)
        - per_page: items per page (default: 20, max: 100)
    """
    category = request.args.get('category')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Limit per_page to reasonable range
    per_page = max(1, min(per_page, 100))

    # Build query
    query = News.query

    if category:
        query = query.filter(News.category == category)

    # Apply sorting
    if sort == 'hottest':
        query = query.order_by(News.hot_score.desc())
    else:
        query = query.order_by(News.published.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [news.to_dict() for news in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    })


@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    """Get single news item by ID."""
    news = News.query.get_or_404(news_id)
    return jsonify(news.to_dict())


# Category order - must match the defined 6-category system
# Order: All (empty), AI, Frontend, Backend, Cloud Native, Blockchain, Other
CATEGORY_ORDER = ['', 'AI', '前端', '后端', '云原生', '区块链', '其他']


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available categories in predefined order."""
    from sqlalchemy import func
    categories = db.session.query(News.category).distinct().all()
    # Filter out None values and flatten the result
    category_list = [cat[0] for cat in categories if cat[0]]
    
    # Sort categories by predefined order
    def get_order(cat):
        try:
            return CATEGORY_ORDER.index(cat)
        except ValueError:
            # Unknown categories go at the end
            return len(CATEGORY_ORDER)
    
    category_list.sort(key=get_order)
    return jsonify(category_list)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


def init_db():
    """Initialize the database and create indexes."""
    with app.app_context():
        db.create_all()
        
        # Create indexes for performance (SQLite doesn't auto-add indexes to existing tables)
        from sqlalchemy import text
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_news_category ON news (category)',
            'CREATE INDEX IF NOT EXISTS idx_news_published ON news (published)',
            'CREATE INDEX IF NOT EXISTS idx_news_hot_score ON news (hot_score)',
            'CREATE INDEX IF NOT EXISTS idx_category_published ON news (category, published)',
            'CREATE INDEX IF NOT EXISTS idx_category_hot_score ON news (category, hot_score)',
        ]
        for idx_sql in indexes:
            try:
                db.session.execute(text(idx_sql))
            except Exception as e:
                print(f"Index creation warning: {e}")
        db.session.commit()
        print("Database initialized with indexes.")


if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5001)
