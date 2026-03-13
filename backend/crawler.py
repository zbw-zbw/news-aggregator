# -*- coding: utf-8 -*-
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
    ],
    '前端圈': [
        {'url': 'https://javascriptweekly.com/rss/', 'name': 'JavaScript Weekly', 'weight': 1.2},
        {'url': 'https://web.dev/feed.xml', 'name': 'web.dev Blog', 'weight': 1.1},
        {'url': 'https://developer.mozilla.org/en-US/blog/rss.xml', 'name': 'MDN Blog', 'weight': 1.1},
        {'url': 'https://fed.taobao.org/atom.xml', 'name': '阿里前端团队', 'weight': 1.1},
        {'url': 'https://www.zhangxinxu.com/wordpress/feed/', 'name': '张鑫旭博客', 'weight': 1.0},
        {'url': 'https://nodeweekly.com/rss/', 'name': 'Node Weekly', 'weight': 1.1},
        {'url': 'https://css-tricks.com/feed/', 'name': 'CSS Tricks', 'weight': 1.0},
        {'url': 'https://frontendfoc.us/rss/', 'name': 'Frontend Focus', 'weight': 1.1},
        {'url': 'http://www.alloyteam.com/feed/', 'name': '腾讯 AlloyTeam', 'weight': 1.0},
    ],
    '后端圈': [
        {'url': 'https://tech.meituan.com/feed/', 'name': '美团技术团队', 'weight': 1.2},
        {'url': 'http://jm.taobao.org/feed.xml', 'name': '阿里中间件', 'weight': 1.1},
        {'url': 'https://insights.thoughtworks.cn/feed/', 'name': 'Thoughtworks 洞见', 'weight': 1.1},
        {'url': 'http://www.ruanyifeng.com/blog/atom.xml', 'name': '阮一峰的网络日志', 'weight': 1.2},
        {'url': 'https://tech.youzan.com/rss/', 'name': '有赞技术团队', 'weight': 1.0},
        {'url': 'https://cloud.tencent.com/developer/devops/feed', 'name': '腾讯技术工程', 'weight': 1.0},
        {'url': 'http://www.alibabatech.com/rss/', 'name': '阿里巴巴技术团队', 'weight': 1.1},
        {'url': 'https://architec.today/feed/', 'name': '高可用架构', 'weight': 1.0},
        {'url': 'https://studygolang.com/rss', 'name': 'Go 语言中文网', 'weight': 1.0},
        {'url': 'https://blog.rust-lang.org/feed.xml', 'name': 'Rust 官方博客', 'weight': 1.1},
    ],
    '云原生圈': [
        {'url': 'https://kubernetes.io/feed.xml', 'name': 'Kubernetes Blog', 'weight': 1.2},
        {'url': 'https://www.cncf.io/blog/feed/', 'name': 'CNCF Blog', 'weight': 1.2},
        {'url': 'https://www.docker.com/blog/feed/', 'name': 'Docker Blog', 'weight': 1.1},
        {'url': 'https://developer.aliyun.com/group/cloudnative/feed', 'name': '阿里云云原生', 'weight': 1.0},
        {'url': 'https://cloud.tencent.com/developer/devops/feed', 'name': '腾讯云原生', 'weight': 1.0},
        {'url': 'https://www.huaweicloud.com/intl/zh-cn/news/cloudnative/rss', 'name': '华为云原生', 'weight': 1.0},
        {'url': 'https://www.openshift.com/blog/feed', 'name': 'OpenShift Blog', 'weight': 1.0},
        {'url': 'https://istio.io/latest/blog/feed.xml', 'name': 'Istio Blog', 'weight': 1.0},
        {'url': 'https://prometheus.io/blog/feed.xml', 'name': 'Prometheus Blog', 'weight': 1.0},
    ],
    '区块链圈': [
        {'url': 'https://app.chaingpt.org/rssfeeds.xml', 'name': 'ChainGPT RSS', 'weight': 1.1},
        {'url': 'https://blog.ethereum.org/feed.xml', 'name': 'Ethereum Blog', 'weight': 1.2},
        {'url': 'https://www.chainnews.com/feed/', 'name': '链闻', 'weight': 1.0},
        {'url': 'https://www.8btc.com/feed', 'name': '巴比特', 'weight': 1.0},
        {'url': 'https://bitcoinmagazine.com/feed', 'name': 'Bitcoin Magazine', 'weight': 1.0},
        {'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/', 'name': 'CoinDesk', 'weight': 1.1},
        {'url': 'https://bihu.com/rss/newest', 'name': '币乎', 'weight': 1.0},
    ],
    'AI+医疗圈': [
        {'url': 'https://arxiv.org/rss/cs.AI', 'name': 'arXiv AI', 'weight': 1.2},
        {'url': 'https://arxiv.org/rss/cs.LG', 'name': 'arXiv ML', 'weight': 1.2},
        {'url': 'https://www.nature.com/natmachintell.rss', 'name': 'Nature Machine Intelligence', 'weight': 1.3},
        {'url': 'https://medicalai.substack.com/feed', 'name': '医学AI前沿博客', 'weight': 1.0},
        {'url': 'https://ai.googleblog.com/feeds/posts/default', 'name': '谷歌AI博客', 'weight': 1.1},
    ],
}

# YouTube RSS Sources (treated as RSS feeds)
YOUTUBE_SOURCES = {
    '技术视频': [
        {'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UC4EKAvw7CZfBPh4a6VlB0zw', 'name': 'Fireship', 'weight': 1.1},
        {'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCYO_jab_esuFRV4b17AJtAw', 'name': '3Blue1Brown', 'weight': 1.0},
        {'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCjfH9h4NpdqH3A-7kY6hRfA', 'name': '尚硅谷', 'weight': 1.0},
        {'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UC8tz_v5p4j5pWmB6JwF8n7Q', 'name': '黑马程序员', 'weight': 1.0},
        {'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UC4JX40jDee_tINbkjycV4Sg', 'name': 'Tech With Tim', 'weight': 1.0},
        {'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UC9-y-6csu5WGm29I7JiwpnA', 'name': 'Computerphile', 'weight': 1.0},
    ]
}

# arXiv RSS Sources (additional categories)
ARXIV_SOURCES = {
    'AI研究': [
        {'url': 'https://arxiv.org/rss/cs.CV', 'name': 'arXiv 计算机视觉', 'weight': 1.2},
        {'url': 'https://arxiv.org/rss/cs.CL', 'name': 'arXiv 自然语言处理', 'weight': 1.2},
        {'url': 'https://arxiv.org/rss/cs.RO', 'name': 'arXiv 机器人技术', 'weight': 1.1},
        {'url': 'https://arxiv.org/rss/stat.ML', 'name': 'arXiv 统计机器学习', 'weight': 1.2},
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

    # Process standard RSS sources
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

    # Process YouTube RSS sources
    for category, sources in YOUTUBE_SOURCES.items():
        print(f"\n--- Processing YouTube category: {category} ---")
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
            time.sleep(1)

    # Process arXiv RSS sources
    for category, sources in ARXIV_SOURCES.items():
        print(f"\n--- Processing arXiv category: {category} ---")
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
            time.sleep(1)

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
