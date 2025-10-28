AppleScript: A Quick Introduction for Your Focus Tool Project
What is AppleScript?
AppleScript is a scripting language built into macOS that lets you control applications and the operating system using English-like commands. Created by Apple in 1993, it's a powerful automation tool that's survived decades of OS updates because it solves a fundamental problem: how do you let different programs talk to each other?
Think of AppleScript as a universal remote control for your Mac. Any application that's "scriptable" (most Mac apps are) exposes certain actions and data that AppleScript can access. You write commands like "tell Application X to do Y" and the OS handles the communication.
Why it matters for your project: You can query Chrome, send notifications, and control system features without needing Swift, Objective-C, or complex APIs. Just call AppleScript from Python using subprocess.
The Basic Pattern
pythonimport subprocess

script = '''
tell application "Application Name"
    -- your commands here
end tell
'''

result = subprocess.run(['osascript', '-e', script], 
                       capture_output=True, text=True)
print(result.stdout)

5 Useful AppleScript Commands for Your Focus Tool
1. Get Active Chrome Tab URL
applescripttell application "Google Chrome"
    get URL of active tab of front window
end tell
Returns the current tab's URL. Useful for real-time checking what the user is viewing.

2. Get All Open Chrome Tab URLs
applescripttell application "Google Chrome"
    set tabList to {}
    repeat with w in windows
        repeat with t in tabs of w
            set end of tabList to URL of t
        end repeat
    end repeat
    return tabList
end tell
Gets every open tab across all Chrome windows. Perfect for checking if distracting sites are open anywhere.

3. Display a Notification
applescriptdisplay notification "Take a break from YouTube!" with title "Focus Check" sound name "Glass"
Sends a native macOS notification. Can include title, message, and sound. No Chrome interaction needed - works system-wide.

4. Display a Dialog Box (more intrusive)
applescriptdisplay dialog "You've been on Reddit for 20 minutes. Continue?" buttons {"Take a Break", "Keep Working"} default button "Take a Break"
Creates a modal popup that requires user interaction. Returns which button was clicked. Use sparingly - very disruptive but effective!

5. Check if Chrome is Running
applescripttell application "System Events"
    set isRunning to (name of processes) contains "Google Chrome"
end tell
return isRunning
Returns true or false. Useful before trying to query Chrome tabs - avoids errors if browser isn't open.

Tips for Your IA

Error Handling: AppleScript commands can fail (app not running, no tabs open). Always check result.returncode in Python.
Performance: AppleScript is slower than direct file access. Use the History DB for historical data, AppleScript for real-time current state.
Documentation: Explain in your IA why you chose each approach - it shows understanding of trade-offs.
Privacy Note: Document that this is a local-only, user-controlled tool. No data leaves the machine.

Good luck with the project, Fanbo! This is a solid IA topic with good technical depth.