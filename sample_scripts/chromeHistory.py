import sqlite3
import os
from pathlib import Path
from datetime import datetime
import shutil

def getRecentChromeHistoryWAL(limit=10):
    """
    Query Chrome's history database for recent visits using WAL read-only mode.
    
    Args:
        limit (int): Number of recent history entries to retrieve
    
    Returns:
        list: List of dicts with 'url', 'title', 'visit_time', and 'visit_count'
              Returns empty list if database not found or on error
    """
    
    # Chrome history location on macOS
    history_path = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome/Default/History"
    )
    
    # Check if history file exists
    if not os.path.exists(history_path):
        print("Chrome history database not found")
        return []
    
    try:
        # Open in read-only mode to avoid locking issues while Chrome is running
        # The '?mode=ro' is crucial - it allows reading while Chrome has the DB open
        db_uri = f"file:{history_path}?mode=ro"
        
        conn = sqlite3.connect(db_uri, uri=True)
        cursor = conn.cursor()
        
        # Chrome stores timestamps as microseconds since January 1, 1601 (!)
        # We need to convert this to Python datetime
        query = """
        SELECT 
            urls.url,
            urls.title,
            urls.visit_count,
            visits.visit_time,
            visits.visit_duration
        FROM urls
        JOIN visits ON urls.id = visits.url
        ORDER BY visits.visit_time DESC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            url, title, visit_count, chrome_time, duration = row
            
            # Convert Chrome's timestamp to Python datetime
            # Chrome time: microseconds since 1601-01-01
            # Python time: seconds since 1970-01-01
            # Difference: 11644473600 seconds
            if chrome_time:
                unix_timestamp = (chrome_time / 1000000) - 11644473600
                visit_datetime = datetime.fromtimestamp(unix_timestamp)
            else:
                visit_datetime = None
            
            history.append({
                'url': url,
                'title': title or '(No title)',
                'visit_time': visit_datetime,
                'visit_count': visit_count,
                'duration_seconds': duration / 1000000 if duration else 0  # microseconds to seconds
            })
        
        conn.close()
        return history
        
    except sqlite3.OperationalError as e:
        print(f"Database error (Chrome might be using it): {e}")
        return []
    except Exception as e:
        print(f"Error reading Chrome history: {e}")
        return []


def getRecentChromeHistoryCopy(limit=10):
    """
    Query Chrome's history database by copying it first.
    Works regardless of WAL mode.
    
    Args:
        limit (int): Number of recent history entries to retrieve
    
    Returns:
        list: List of dicts with 'url', 'title', 'visit_time', and 'visit_count'
    """
    
    history_path = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome/Default/History"
    )
    
    if not os.path.exists(history_path):
        print("Chrome history database not found")
        return []
    
    try:
        # Copy the database to temp location
        # This avoids all locking issues
        temp_path = "/tmp/chrome_history_copy.db"
        shutil.copy2(history_path, temp_path)
        
        # Also copy journal file if it exists (for consistency)
        journal_path = history_path + "-journal"
        if os.path.exists(journal_path):
            shutil.copy2(journal_path, temp_path + "-journal")
        
        # Now query the copy
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            urls.url,
            urls.title,
            urls.visit_count,
            visits.visit_time,
            visits.visit_duration
        FROM urls
        JOIN visits ON urls.id = visits.url
        ORDER BY visits.visit_time DESC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            url, title, visit_count, chrome_time, duration = row
            
            # Convert Chrome's timestamp
            if chrome_time:
                unix_timestamp = (chrome_time / 1000000) - 11644473600
                visit_datetime = datetime.fromtimestamp(unix_timestamp)
            else:
                visit_datetime = None
            
            history.append({
                'url': url,
                'title': title or '(No title)',
                'visit_time': visit_datetime,
                'visit_count': visit_count,
                'duration_seconds': duration / 1000000 if duration else 0
            })
        
        conn.close()
        
        # Clean up temp files
        os.remove(temp_path)
        if os.path.exists(temp_path + "-journal"):
            os.remove(temp_path + "-journal")
        
        return history
        
    except Exception as e:
        print(f"Error reading Chrome history: {e}")
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return []


def formatTimeDelta(visit_datetime):
    """Helper function to show how recent a visit was"""
    if not visit_datetime:
        return "Unknown time"
    
    delta = datetime.now() - visit_datetime
    
    if delta.seconds < 60:
        return f"{delta.seconds} seconds ago"
    elif delta.seconds < 3600:
        return f"{delta.seconds // 60} minutes ago"
    elif delta.days == 0:
        return f"{delta.seconds // 3600} hours ago"
    else:
        return f"{delta.days} days ago"


# Example usage:
if __name__ == "__main__":
    print("Recent Chrome browsing history:\n")
    print("=" * 80)
    
    history = getRecentChromeHistoryCopy(limit=10) #check different fdunctions
    
    if history:
        for i, entry in enumerate(history, 1):
            print(f"\n{i}. {entry['title']}")
            print(f"   URL: {entry['url']}")
            print(f"   Time: {entry['visit_time'].strftime('%Y-%m-%d %H:%M:%S') if entry['visit_time'] else 'Unknown'}")
            print(f"   Recency: {formatTimeDelta(entry['visit_time'])}")
            print(f"   Total visits to this URL: {entry['visit_count']}")
            print(f"   Duration: {entry['duration_seconds']:.1f} seconds")
    else:
        print("No history found or unable to read database")
    
    print("\n" + "=" * 80)
    
    # Demo: Check for recent visits to distracting sites
    print("\n🔍 Checking for recent distractions...\n")
    
    distracting_domains = ['youtube.com', 'reddit.com', 'twitter.com', 'instagram.com']
    recent_distractions = [
        entry for entry in history 
        if any(domain in entry['url'] for domain in distracting_domains)
    ]
    
    if recent_distractions:
        print(f"⚠️  Found {len(recent_distractions)} recent visits to distracting sites:")
        for entry in recent_distractions:
            domain = next(d for d in distracting_domains if d in entry['url'])
            print(f"  - {domain}: {formatTimeDelta(entry['visit_time'])}")
    else:
        print("✅ No recent distractions detected!")