import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import multiprocessing
import threading
from win32con import VK_SHIFT
import sv_ttk
import easing_functions
from SmoothedScroll import SmoothedScroll, SmoothedScrollConfig, AppConfig, ScrollConfig
from utils.steam_blocklist import find_steam_games
import pystray
from pystray import MenuItem as item
from PIL import Image
import win32gui
import win32process
import psutil

CONFIG_FILE_PATH = "./assets/config.json"
DEFAULT_CONFIG = {
    "theme": "dark",
    "scroll_distance": 120,
    "acceleration": 1.0,
    "opposite_acceleration": 1.2,
    "acceleration_delta": 70,
    "acceleration_max": 14,
    "scroll_duration": 500,
    "pulse_scale": 3.0,
    "inverted_scroll": False
}

def smoothed_scroll_task(config: SmoothedScrollConfig):
    try:
        smoothed_scroll_instance = SmoothedScroll(config=config)
        smoothed_scroll_instance.start(is_block=True)
    except Exception as e:
        print(f"Error in SmoothedScroll process: {e}")

class ScrollConfigApp:
    def __init__(self):
        self.config = self.load_config()
        self.root = tk.Tk()
        self.root.title("Smoothed Scroll GUI")
        self.root.iconbitmap("./assets/icon.ico")
        self.root.geometry("400x790")
        self.root.resizable(False, False)
        self.center_window()
        sv_ttk.set_theme(self.config.get("theme", "dark"))
        self.distance_var = tk.IntVar(value=self.config.get("scroll_distance", 120))
        self.acceleration_var = tk.DoubleVar(value=self.config.get("acceleration", 1.0))
        self.opposite_acceleration_var = tk.DoubleVar(value=self.config.get("opposite_acceleration", 1.2))
        self.acceleration_delta_var = tk.IntVar(value=self.config.get("acceleration_delta", 70))
        self.acceleration_max_var = tk.IntVar(value=self.config.get("acceleration_max", 14))
        self.duration_var = tk.IntVar(value=self.config.get("scroll_duration", 500))
        self.pulse_scale_var = tk.DoubleVar(value=self.config.get("pulse_scale", 3.0))
        self.inverted_scroll_var = tk.BooleanVar(value=self.config.get("inverted_scroll", False))
        self.theme_var = tk.StringVar(value=self.config.get("theme", "dark"))
        self.smoothed_scroll_process = None
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_gui(self):
        frame = ttk.LabelFrame(self.root, text="Scroll Settings")
        frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(frame, text="Scroll Distance (px):").pack(anchor="w", padx=5, pady=5)
        ttk.Spinbox(frame, from_=0, to=2000, textvariable=self.distance_var).pack(anchor="w", fill="x", padx=5, pady=5)
        ttk.Label(frame, text="Acceleration (x):").pack(anchor="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.acceleration_var).pack(anchor="w", fill="x", padx=5, pady=5)
        ttk.Label(frame, text="Opposite Acceleration (x):").pack(anchor="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.opposite_acceleration_var).pack(anchor="w", fill="x", padx=5, pady=5)
        ttk.Label(frame, text="Acceleration Delta (ms):").pack(anchor="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.acceleration_delta_var).pack(anchor="w", fill="x", padx=5, pady=5)
        ttk.Label(frame, text="Max Acceleration Steps:").pack(anchor="w", padx=5, pady=5)
        ttk.Spinbox(frame, from_=0, to=30, textvariable=self.acceleration_max_var).pack(anchor="w", fill="x", padx=5, pady=5)
        ttk.Label(frame, text="Scroll Duration (ms):").pack(anchor="w", padx=5, pady=5)
        ttk.Spinbox(frame, from_=0, to=1000, textvariable=self.duration_var).pack(anchor="w", fill="x", padx=5, pady=5)
        ttk.Label(frame, text="Pulse Scale (x):").pack(anchor="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.pulse_scale_var).pack(anchor="w", fill="x", padx=5, pady=5)
        ttk.Checkbutton(frame, text="Inverted Scroll", variable=self.inverted_scroll_var).pack(anchor="w", padx=5, pady=5)
        theme_frame = ttk.LabelFrame(self.root, text="Theme Settings")
        theme_frame.pack(padx=10, pady=10, fill="x")
        ttk.Radiobutton(theme_frame, text="Dark Theme", variable=self.theme_var, value="dark", command=self.apply_theme).pack(anchor="w", padx=5, pady=5)
        ttk.Radiobutton(theme_frame, text="Light Theme", variable=self.theme_var, value="light", command=self.apply_theme).pack(anchor="w", padx=5, pady=5)

        self.action_button = ttk.Button(frame, text="Start Smoothed Scroll", command=self.toggle_smoothed_scroll)
        self.action_button.pack(fill="x", pady=5)
        ttk.Button(frame, text="Reset to Default", command=self.reset_to_default).pack(fill="x", pady=5)

    def toggle_smoothed_scroll(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            self.stop_smoothed_scroll()
        else:
            self.apply_settings()

    def apply_settings(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            self.stop_smoothed_scroll()
        self.save_config()
        self.start_smoothed_scroll()

    def apply_theme(self):
        theme = self.theme_var.get()
        sv_ttk.set_theme(theme)
        self.config["theme"] = theme
        self.save_config()

    def start_smoothed_scroll(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            return

        app_configs = [
            AppConfig(
                regexp=r'.*',
                scroll_config=ScrollConfig(
                    distance=self.distance_var.get(),
                    acceleration=self.acceleration_var.get(),
                    opposite_acceleration=self.opposite_acceleration_var.get(),
                    acceleration_delta=self.acceleration_delta_var.get(),
                    acceleration_max=self.acceleration_max_var.get(),
                    duration=self.duration_var.get(),
                    pulse_scale=self.pulse_scale_var.get(),
                    ease=easing_functions.LinearInOut,
                    inverted=self.inverted_scroll_var.get(),
                    horizontal_scroll_key=VK_SHIFT
                ),
            )
        ]

        smoothed_scroll_config = SmoothedScrollConfig(app_config=app_configs)

        self.smoothed_scroll_process = multiprocessing.Process(
            target=smoothed_scroll_task,
            args=(smoothed_scroll_config,),
            daemon=True
        )
        self.smoothed_scroll_process.start()

        threading.Thread(target=find_steam_games, daemon=True).start()
        self.action_button.config(text="Stop Smoothed Scroll")

    def stop_smoothed_scroll(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            try:
                self.smoothed_scroll_process.terminate()
                self.smoothed_scroll_process.join(timeout=5)
            except Exception as e:
                print(f"Error terminating SmoothedScroll process: {e}")
            finally:
                self.smoothed_scroll_process = None
                self.action_button.config(text="Start Smoothed Scroll")

    def load_config(self):
        if not os.path.exists(CONFIG_FILE_PATH):
            return DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE_PATH, 'r') as file:
                config = json.load(file)
                return config
        except (json.JSONDecodeError, FileNotFoundError):
            return DEFAULT_CONFIG

    def save_config(self):
        config = {
            "theme": self.config["theme"],
            "scroll_distance": self.distance_var.get(),
            "acceleration": self.acceleration_var.get(),
            "opposite_acceleration": self.opposite_acceleration_var.get(),
            "acceleration_delta": self.acceleration_delta_var.get(),
            "acceleration_max": self.acceleration_max_var.get(),
            "scroll_duration": self.duration_var.get(),
            "pulse_scale": self.pulse_scale_var.get(),
            "inverted_scroll": self.inverted_scroll_var.get(),
            "message_shown": self.config.get("message_shown", False)
        }
        with open(CONFIG_FILE_PATH, 'w') as file:
            json.dump(config, file, indent=4)

    def reset_to_default(self):
        self.config = DEFAULT_CONFIG
        self.distance_var.set(self.config["scroll_distance"])
        self.acceleration_var.set(self.config["acceleration"])
        self.opposite_acceleration_var.set(self.config["opposite_acceleration"])
        self.acceleration_delta_var.set(self.config["acceleration_delta"])
        self.acceleration_max_var.set(self.config["acceleration_max"])
        self.duration_var.set(self.config["scroll_duration"])
        self.pulse_scale_var.set(self.config["pulse_scale"])
        self.inverted_scroll_var.set(self.config["inverted_scroll"])
        self.theme_var.set(self.config["theme"])
        self.apply_theme()

    def on_closing(self):
        self.stop_smoothed_scroll()
        if not self.config.get("message_shown", False):
            messagebox.showinfo(
                "Smoothed Scroll",
                "Smoothed Scroll is running from the system tray."
            )
            self.config["message_shown"] = True
            self.save_config()
        self.root.destroy()

def start_gui_app():
    multiprocessing.freeze_support()
    app = ScrollConfigApp()
    app.root.mainloop()

BLOCKLIST_PATH = './assets/blocklist.json'
ICON_PATH = './assets/icon.ico'  

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

def toggle_blocklist(icon, process_name):
    blocklist = load_blocklist()
    process_name = str(process_name)
    if process_name in blocklist:
        blocklist.remove(process_name)
    else:
        blocklist.append(process_name)
    write_blocklist(blocklist)
    refresh_menu(icon)

def refresh_menu(icon, interval=5):
    open_processes = get_open_process_names()
    blocklist = load_blocklist()
    exceptions_menu = [item(process, lambda _, p=process: toggle_blocklist(icon, p), 
                             checked=lambda item, p=process: p in blocklist) for process in open_processes]
    icon.menu = pystray.Menu(
        item('Exceptions', pystray.Menu(*exceptions_menu)),
        item('Open Settings', lambda _: open_gui(icon)),
        item('Exit', lambda: stop_icon(icon))
    )
    icon.update_menu()
    threading.Timer(interval, refresh_menu, [icon]).start()


def stop_icon(icon):
    icon.stop()

def open_gui(icon):
    icon.stop()
    threading.Thread(target=start_gui_app).start()

def run_tray():
    icon_image = load_icon()
    if icon_image is None:
        return

    icon = pystray.Icon("SmoothedScroll", icon_image, "Smoothed Scroll")
    refresh_menu(icon)
    icon.run()

def start_taskbar_icon():
    directory = os.path.dirname(BLOCKLIST_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    if not os.path.exists(BLOCKLIST_PATH):
        write_blocklist([])  
    else:
        try:
            blocklist = load_blocklist()
            if not isinstance(blocklist, list):
                write_blocklist([])
        except Exception:
            write_blocklist([])

if __name__ == "__main__":
    gui_thread = threading.Thread(target=start_gui_app)
    tray_thread = threading.Thread(target=run_tray)
    gui_thread.start()
    tray_thread.start()
    gui_thread.join()
    tray_thread.join()