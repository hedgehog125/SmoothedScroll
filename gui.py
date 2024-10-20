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

CONFIG_FILE_PATH = "./assets/config.json"
DEFAULT_CONFIG = {
    "theme": "dark",
    "mode": "light",
    "scroll_distance": 120,
    "acceleration": 1.0,
    "opposite_acceleration": 1.2,
    "acceleration_delta": 70,
    "acceleration_max": 14,
    "scroll_duration": 500,
    "pulse_scale": 3.0,
    "inverted_scroll": False,
    "message_shown": False
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
        self.root.geometry("400x750")
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

        ttk.Button(frame, text="Apply Settings", command=self.apply_settings).pack(fill="x", pady=5)
        ttk.Button(frame, text="Start Smoothed Scroll", command=self.start_smoothed_scroll).pack(fill="x", pady=5)
        ttk.Button(frame, text="Stop Smoothed Scroll", command=self.stop_smoothed_scroll).pack(fill="x", pady=5)
        ttk.Button(frame, text="Reset to Default", command=self.reset_to_default).pack(fill="x", pady=5)

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

        disabled_apps = self.load_disabled_apps()

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

        for app in disabled_apps:
            app_configs.append(AppConfig(
                regexp=rf'.*{app}.*',
                enabled=False
            ))

        smoothed_scroll_config = SmoothedScrollConfig(app_config=app_configs)

        self.smoothed_scroll_process = multiprocessing.Process(
            target=smoothed_scroll_task,
            args=(smoothed_scroll_config,),
            daemon=True
        )
        self.smoothed_scroll_process.start()

        threading.Thread(target=find_steam_games, daemon=True).start()

    def stop_smoothed_scroll(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            try:
                self.smoothed_scroll_process.terminate()
                self.smoothed_scroll_process.join(timeout=5)
            except Exception as e:
                print(f"Error terminating SmoothedScroll process: {e}")
            finally:
                self.smoothed_scroll_process = None

    def load_disabled_apps(self):
        blocklist_path = './assets/blocklist.json'
        if not os.path.exists(blocklist_path):
            return []

        try:
            with open(blocklist_path, 'r') as file:
                data = file.read().strip()
                if not data:
                    return []
                return json.loads(data)
        except json.JSONDecodeError:
            return []
        except Exception:
            return []

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
            "mode": self.config["mode"],
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

