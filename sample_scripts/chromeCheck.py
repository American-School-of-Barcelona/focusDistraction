import subprocess
import json

def getCurrentChromeTabs():
    """
    Get all open Chrome tabs across all windows.
    
    Returns:
        list: List of dicts with 'url', 'title', and 'window_index' for each tab
              Returns empty list if Chrome isn't running or on error
    """
    
    applescript = '''
    tell application "Google Chrome"
        set tabList to {}
        set windowIndex to 1
        repeat with w in windows
            repeat with t in tabs of w
                set tabInfo to {tabURL:URL of t, tabTitle:title of t, windowNum:windowIndex}
                set end of tabList to tabInfo
            end repeat
            set windowIndex to windowIndex + 1
        end repeat
        
        -- Convert to JSON-like string for easier Python parsing
        set output to ""
        repeat with tabInfo in tabList
            set output to output & (tabURL of tabInfo) & "|" & (tabTitle of tabInfo) & "|" & (windowNum of tabInfo) & "\\n"
        end repeat
        return output
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=5  # Don't hang forever
        )
        
        # Check if command succeeded
        if result.returncode != 0:
            print(f"AppleScript error: {result.stderr}")
            return []
        
        # Parse the output
        tabs = []
        for line in result.stdout.strip().split('\n'):
            if line:  # Skip empty lines
                parts = line.split('|')
                if len(parts) == 3:
                    tabs.append({
                        'url': parts[0],
                        'title': parts[1],
                        'window': int(parts[2])
                    })
        
        return tabs
        
    except subprocess.TimeoutExpired:
        print("Chrome query timed out")
        return []
    except Exception as e:
        print(f"Error getting Chrome tabs: {e}")
        return []


# Example usage:
if __name__ == "__main__":
    tabs = getCurrentChromeTabs()
    
    if tabs:
        print(f"Found {len(tabs)} open tabs:\n")
        for tab in tabs:
            print(f"Window {tab['window']}: {tab['title']}")
            print(f"  → {tab['url']}\n")
    else:
        print("No Chrome tabs found (or Chrome not running)")
    
    # Check for distracting sites
    distracting_domains = ['youtube.com', 'reddit.com', 'twitter.com', 'instagram.com']
    distractions = [tab for tab in tabs if any(domain in tab['url'] for domain in distracting_domains)]
    
    if distractions:
        print(f"⚠️  Found {len(distractions)} potentially distracting tabs!")
        for tab in distractions:
            print(f"  - {tab['title']}")