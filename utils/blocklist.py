import json
import os
import time
import psutil
import win32gui
import win32process

BLOCKLIST_PATH = os.path.join(os.getenv('APPDATA'), 'SmoothedScroll', 'blocklist.json')

def load_blocklist():
    if not os.path.exists(BLOCKLIST_PATH):
        return []
    try:
        with open(BLOCKLIST_PATH, 'r', encoding='utf-8') as file:
            data = file.read().strip()
            if not data:
                return []
            blocklist = json.loads(data)
            if not isinstance(blocklist, list):
                return []
            return [str(item) for item in blocklist]
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Unexpected error loading blocklist: {e}")
        return []

def write_blocklist(blocklist):
    try:
        with open(BLOCKLIST_PATH, 'w', encoding='utf-8') as file:
            json.dump(blocklist, file, indent=2)
    except Exception as e:
        print(f"Failed to save blocklist: {e}")

def toggle_blocklist(process_name):
    blocklist = load_blocklist()
    process_name = str(process_name)
    if process_name in blocklist:
        blocklist.remove(process_name)
    else:
        blocklist.append(process_name)
    write_blocklist(blocklist)
    return blocklist

def blocklist_loop(app):
    blocklist = load_blocklist()
    while True:
        active_process_id = win32process.GetWindowThreadProcessId(
            win32gui.GetForegroundWindow()
        )[1]
        active_name = psutil.Process(active_process_id).name()

        app.smoothed_scroll_blocked_by_app = active_name in blocklist
        app.start_or_stop_smoothed_scroll()

        time.sleep(1)