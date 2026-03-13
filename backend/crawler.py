"""
RSS Crawler for the news aggregator.
Fetches news from predefined RSS sources and stores them in the database.
"""
import feedparser
import requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from models import db, News
from app import app
import time

# RSS Sources configuration
RSS_SOURCES = {
    '程序员圈': [
        {'url': 'https://tech.meituan.com/feed/', 'name': '美团技术团队', 'weight': 1.1},
        {'url': 'https://developer.mozilla.org/en-US/blog/rss.xml', 'name': 'MDN Blog', 'weight': 1.0},
        {'url': 'https://web.dev/feed.xml', 'name': 'web.dev', 'weight': 1.0},
        {'url': 'https://devblogs.microsoft.com/dotnet/feed/', 'name': 'Microsoft .NET Blog', 'weight': 1.1},
        {'url': 'https://news.ycombinator.com/rss', 'name': 'Hacker News', 'weight': 1.2},
        {'url': 'https://www.reddit.com/r/programming/.rss', 'name': 'Reddit r/programming', 'weight': 1.0},
        {'url': 'https://www.oschina.net/news/rss', 'name': '开源中国', 'weight': 1.0},
        {'url': 'https://www.infoq.cn/feed', 'name': 'InfoQ', 'weight': 1.1},
        {'url': 'https://developer.aliyun.com/feed', 'name': '阿里云开发者社区', 'weight': 1.0},
        {'url': 'https://cloud.tencent.com/developer/devops/feed', 'name': '腾讯云开发者社区', 'weight': 1.0},
    ],
    'AI圈': [
        {'url': 'https://openai.com/blog/rss.xml', 'name': 'OpenAI Blog', 'weight': 1.3},
        {'url': 'https://blog.google/technology/ai/rss/', 'name': 'Google AI Blog', 'weight': 1.2},
        {'url': 'https://deepmind.google/discover/blog/rss/', 'name': 'DeepMind Blog', 'weight': 1.2},
        {'url': 'https://huggingface.co/blog/feed.xml', 'name': 'Hugging Face Blog', 'weight': 1.1},
        {'url': 'https://towardsdatascience.com/feed', 'name': 'Towards Data Science', 'weight': 1.0},
        {'url': 'https://jalammar.github.io/feed.xml', 'name': "Jay Alammar's Blog", 'weight': 1.0},
        {'url': 'https://bair.berkeley.edu/blog/feed.xml', 'name': 'BAIR', 'weight': 1.1},
        {'url': 'https://ai.meta.com/blog/rss/', 'name': 'Meta AI Blog', 'weight': 1.1},
    ]
}

# User agent for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def parse_date(entry):
    """Parse publication date from RSS entry."""
    try:
        # Try different date fields
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        elif hasattr(entry, 'published') and entry.published:
            return date_parser.parse(entry.published)
        elif hasattr(entry, 'updated') and entry.updated:
            return date_parser.parse(entry.updated)
    except Exception as e:
        print(f"Error parsing date: {e}")
    return datetime.utcnow()


def calculate_hot_score(published_date, source_weight):
    """
    Calculate hot score based on time decay and source weight.
    Formula: hot_score = 1 / (hours_since_published + 2) * source_weight
    """
    try:
        hours_since = (datetime.utcnow() - published_date).total_seconds() / 3600
        hours_since = max(0, hours_since)
        hot_score = 1 / (hours_since + 2) * source_weight
        return round(hot_score, 4)
    except Exception:
        return 0.0


def truncate_summary(summary, max_length=500):
    """Truncate summary to max_length characters."""
    if not summary:
        return ''
    # Remove HTML tags
    import re
    clean = re.sub(r'<[^>]+>', '', summary)
    if len(clean) > max_length:
        return clean[:max_length] + '...'
    return clean


def fetch_rss_feed(url, source_name, category, weight):
    """Fetch and parse a single RSS feed."""
    print(f"Fetching: {source_name} ({url})")
    articles = []

    try:
        # Use requests to get the content first (better for some sites)
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        # Parse the feed
        feed = feedparser.parse(response.content)

        if feed.bozo and feed.bozo_exception:
            print(f"Warning: Feed parsing issue for {source_name}: {feed.bozo_exception}")

        for entry in feed.entries:
            try:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))

                if not link:
                    continue

                published_date = parse_date(entry)
                hot_score = calculate_hot_score(published_date, weight)

                articles.append({
                    'title': title,
                    'link': link,
                    'summary': truncate_summary(summary),
                    'published': published_date,
                    'source': source_name,
                    'category': category,
                    'hot_score': hot_score
                })
            except Exception as e:
                print(f"Error processing entry: {e}")
                continue

        print(f"  Found {len(articles)} articles from {source_name}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {source_name}: {e}")
    except Exception as e:
        print(f"Unexpected error for {source_name}: {e}")

    return articles


def save_articles(articles):
    """Save articles to database, skipping duplicates."""
    added = 0
    skipped = 0

    for article in articles:
        try:
            # Check if article already exists
            existing = News.query.filter_by(link=article['link']).first()
            if existing:
                skipped += 1
                continue

            news = News(
                title=article['title'],
                summary=article['summary'],
                link=article['link'],
                published=article['published'],
                source=article['source'],
                category=article['category'],
                hot_score=article['hot_score']
            )
            db.session.add(news)
            added += 1
        except Exception as e:
            print(f"Error saving article {article['link']}: {e}")

    db.session.commit()
    return added, skipped


def cleanup_old_news(days=30):
    """Remove news older than specified days."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    old_news = News.query.filter(News.published < cutoff_date)
    count = old_news.count()
    old_news.delete()
    db.session.commit()
    print(f"Cleaned up {count} old news articles (older than {days} days)")


def run_crawler():
    """Main crawler function."""
    print("=" * 50)
    print(f"Starting crawler at {datetime.utcnow().isoformat()}")
    print("=" * 50)

    total_added = 0
    total_skipped = 0

    for category, sources in RSS_SOURCES.items():
        print(f"\n--- Processing category: {category} ---")
        for source in sources:
            articles = fetch_rss_feed(
                source['url'],
                source['name'],
                category,
                source['weight']
            )
            added, skipped = save_articles(articles)
            total_added += added
            total_skipped += skipped
            time.sleep(1)  # Be polite to servers

    # Cleanup old news (keep last 7 days)
    print("\n--- Cleaning up old news ---")
    cleanup_old_news(7)

    print("\n" + "=" * 50)
    print(f"Crawler finished!")
    print(f"Total added: {total_added}")
    print(f"Total skipped (duplicates): {total_skipped}")
    print("=" * 50)


if __name__ == '__main__':
    with app.app_context():
        run_crawler()
