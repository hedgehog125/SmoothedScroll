import pystray
from pystray import MenuItem as item
from PIL import Image
import json
import os
import win32gui
import win32process
import psutil

BLOCKLIST_PATH = './assets/blocklist.json'
ICON_PATH = './assets/icon.ico'  
TOAST_DURATION = 5  

def load_icon():
    try:
        return Image.open(ICON_PATH)
    except Exception as e:
        print(f"Error loading icon: {e}")
        return None

def get_open_process_names():
    def enum_window_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                results.add(process_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    processes = set()
    win32gui.EnumWindows(enum_window_callback, processes)
    return sorted(processes)

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
                print("Blocklist is not a list. Resetting to empty list.")
                return []

            blocklist = [str(item) for item in blocklist]
            return blocklist
    except json.JSONDecodeError:

        print("JSON decode error in blocklist.json. Resetting to empty list.")
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

def toggle_blocklist(icon, process_name):
    blocklist = load_blocklist()
    process_name = str(process_name)  
    print(f"Process to toggle: {process_name}")  
    write_blocklist(blocklist)  
    refresh_menu(icon)

def refresh_menu(icon):
    open_processes = get_open_process_names()
    blocklist = load_blocklist()
    exceptions_menu = []
    for process in open_processes:

        exceptions_menu.append(
            item(
                process,
                lambda _, p=process: toggle_blocklist(icon, p),
                checked=lambda item, p=process: p in blocklist
            )
        )

    icon.menu = pystray.Menu(
        item('Exceptions', pystray.Menu(*exceptions_menu)),
        item('Refresh', lambda: refresh_menu(icon)),
        item('Close', lambda: stop_icon(icon))
    )
    icon.update_menu()

def stop_icon(icon):
    icon.stop()

def run_tray():
    icon_image = load_icon()
    if icon_image is None:
        print("Icon could not be loaded, exiting.")
        return

    icon = pystray.Icon("SmoothedScroll", icon_image, "Smoothed Scroll")
    refresh_menu(icon)  
    icon.run()

def start_taskbar_icon():
    if not os.path.exists(BLOCKLIST_PATH):
        os.makedirs(os.path.dirname(BLOCKLIST_PATH), exist_ok=True)
        write_blocklist([])  
    else:
        try:
            blocklist = load_blocklist()
            if not isinstance(blocklist, list):
                print("Blocklist is not a list. Resetting to empty list.")
                write_blocklist([])
        except Exception:
            write_blocklist([])  

    run_tray()  