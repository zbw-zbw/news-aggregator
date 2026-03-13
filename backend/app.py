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


@app.route('/api/news', methods=['GET'])
def get_news():
    """
    Get paginated news list.
    Query params:
        - category: '程序员圈' or 'AI圈' (optional)
        - sort: 'newest' or 'hottest' (default: newest)
        - page: page number (default: 1)
    """
    category = request.args.get('category')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = 20

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


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available categories."""
    return jsonify(['程序员圈', 'AI圈'])


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database initialized.")


if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5001)
