# -*- coding: utf-8 -*-
"""
Maintenance script for the news aggregator.
Provides utilities for data cleanup, health checks, and reporting.
"""
import argparse
import requests
import feedparser
from datetime import datetime, timedelta
from models import db, News
from app import app
import time

# User agent for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def cleanup_old_news(days=30):
    """Remove news older than specified days."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    old_news = News.query.filter(News.published < cutoff_date)
    count = old_news.count()
    old_news.delete()
    db.session.commit()
    print(f"Cleaned up {count} old news articles (older than {days} days)")
    return count


def check_rss_health(url, name):
    """Check if an RSS source is accessible."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        entry_count = len(feed.entries)
        return {
            'name': name,
            'url': url,
            'status': 'ok',
            'entries': entry_count,
            'error': None
        }
    except Exception as e:
        return {
            'name': name,
            'url': url,
            'status': 'error',
            'entries': 0,
            'error': str(e)
        }


def check_all_sources():
    """Check health of all RSS sources."""
    from crawler import RSS_SOURCES, YOUTUBE_SOURCES

    print("=" * 60)
    print("RSS Source Health Check")
    print("=" * 60)

    results = []

    # Check RSS sources
    for category, sources in RSS_SOURCES.items():
        print(f"\n--- Category: {category} ---")
        for source in sources:
            result = check_rss_health(source['url'], source['name'])
            results.append(result)
            status_icon = "✓" if result['status'] == 'ok' else "✗"
            print(f"  {status_icon} {result['name']}: {result['entries']} entries")
            if result['error']:
                print(f"    Error: {result['error']}")
            time.sleep(0.5)  # Be polite to servers

    # Check YouTube sources
    print(f"\n--- YouTube Channels ---")
    for category, sources in YOUTUBE_SOURCES.items():
        for source in sources:
            result = check_rss_health(source['url'], source['name'])
            results.append(result)
            status_icon = "✓" if result['status'] == 'ok' else "✗"
            print(f"  {status_icon} {result['name']}: {result['entries']} entries")
            if result['error']:
                print(f"    Error: {result['error']}")
            time.sleep(0.5)

    # Summary
    ok_count = sum(1 for r in results if r['status'] == 'ok')
    error_count = len(results) - ok_count

    print("\n" + "=" * 60)
    print(f"Summary: {ok_count} OK, {error_count} Errors")
    print("=" * 60)

    return results


def generate_stats():
    """Generate database statistics."""
    from sqlalchemy import func

    print("=" * 60)
    print("Database Statistics")
    print("=" * 60)

    # Total count
    total = News.query.count()
    print(f"\nTotal news articles: {total}")

    # Count by category
    print("\n--- By Category ---")
    category_counts = db.session.query(
        News.category,
        func.count(News.id)
    ).group_by(News.category).all()

    for category, count in sorted(category_counts, key=lambda x: -x[1]):
        print(f"  {category or 'Uncategorized'}: {count}")

    # Count by source type
    print("\n--- By Source Type ---")
    type_counts = db.session.query(
        News.source_type,
        func.count(News.id)
    ).group_by(News.source_type).all()

    for source_type, count in sorted(type_counts, key=lambda x: -x[1]):
        print(f"  {source_type}: {count}")

    # Count by video
    video_count = News.query.filter(News.is_video == True).count()
    print(f"\nVideo articles: {video_count}")

    # Recent additions (last 24 hours)
    recent = News.query.filter(
        News.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    print(f"Added in last 24 hours: {recent}")

    # Oldest and newest
    oldest = News.query.order_by(News.published.asc()).first()
    newest = News.query.order_by(News.published.desc()).first()

    if oldest and newest:
        print(f"\nDate range: {oldest.published.date()} to {newest.published.date()}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='News Aggregator Maintenance')
    parser.add_argument('--cleanup', action='store_true',
                        help='Clean up old news (default: 30 days)')
    parser.add_argument('--cleanup-days', type=int, default=30,
                        help='Number of days to keep (default: 30)')
    parser.add_argument('--health-check', action='store_true',
                        help='Check RSS source health')
    parser.add_argument('--stats', action='store_true',
                        help='Show database statistics')
    parser.add_argument('--all', action='store_true',
                        help='Run all maintenance tasks')

    args = parser.parse_args()

    with app.app_context():
        if args.all or args.cleanup:
            cleanup_old_news(args.cleanup_days)

        if args.all or args.health_check:
            check_all_sources()

        if args.all or args.stats:
            generate_stats()

        if not any([args.all, args.cleanup, args.health_check, args.stats]):
            parser.print_help()


if __name__ == '__main__':
    main()
