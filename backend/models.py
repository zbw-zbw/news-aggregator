"""
Database models for the news aggregator.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class News(db.Model):
    """News article model."""
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    link = db.Column(db.Text, unique=True, nullable=False)
    published = db.Column(db.DateTime, index=True)
    source = db.Column(db.Text)
    category = db.Column(db.Text, index=True)
    hot_score = db.Column(db.Float, default=0.0, index=True)
    is_video = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite indexes for common query patterns
    __table_args__ = (
        db.Index('idx_category_published', 'category', 'published'),
        db.Index('idx_category_hot_score', 'category', 'hot_score'),
    )

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'link': self.link,
            'source': self.source,
            'published': self.published.isoformat() if self.published else None,
            'category': self.category,
            'hot_score': self.hot_score,
            'is_video': self.is_video
        }

    def __repr__(self):
        return f'<News {self.id}: {self.title[:50]}...>'
