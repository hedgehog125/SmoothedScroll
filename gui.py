import multiprocessing
import tkinter as tk
from tkinter import messagebox
import json
import os
import threading  
from win32con import VK_SHIFT

import TKinterModernThemes as TKMT
import easing_functions
from SmoothedScroll import SmoothedScroll, SmoothedScrollConfig, AppConfig, ScrollConfig
from utils.steam_blocklist import find_steam_games

CONFIG_FILE_PATH = "./assets/config.json"
DEFAULT_CONFIG = {
    "theme": "sun-valley",
    "mode": "light",
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

class ScrollConfigApp(TKMT.ThemedTKinterFrame):
    def __init__(self):
        self.config = self.load_config()

        super().__init__("Smoothed Scroll Configuration", self.config["theme"], self.config["mode"])
        self.root.iconbitmap("./assets/icon.ico")

        self.distance_var = tk.IntVar(value=self.config.get("scroll_distance", 120))
        self.acceleration_var = tk.DoubleVar(value=self.config.get("acceleration", 1.0))
        self.opposite_acceleration_var = tk.DoubleVar(value=self.config.get("opposite_acceleration", 1.2))
        self.acceleration_delta_var = tk.IntVar(value=self.config.get("acceleration_delta", 70))
        self.acceleration_max_var = tk.IntVar(value=self.config.get("acceleration_max", 14))
        self.duration_var = tk.IntVar(value=self.config.get("scroll_duration", 500))
        self.pulse_scale_var = tk.DoubleVar(value=self.config.get("pulse_scale", 3.0))
        self.inverted_scroll_var = tk.BooleanVar(value=self.config.get("inverted_scroll", False))

        self.smoothed_scroll_process = None
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.run()

    def setup_gui(self):
        scroll_frame = self.addLabelFrame("Scroll Settings")
        scroll_frame.Label("Scroll Distance (px):")
        scroll_frame.NumericalSpinbox(0, 2000, 100, self.distance_var)
        scroll_frame.Label("Acceleration (x):")
        scroll_frame.Entry(self.acceleration_var)
        scroll_frame.Label("Opposite Acceleration (x):")
        scroll_frame.Entry(self.opposite_acceleration_var)
        scroll_frame.Label("Acceleration Delta (ms):")
        scroll_frame.Entry(self.acceleration_delta_var)
        scroll_frame.Label("Max Acceleration Steps:")
        scroll_frame.NumericalSpinbox(0, 30, 1, self.acceleration_max_var)
        scroll_frame.Label("Scroll Duration (ms):")
        scroll_frame.NumericalSpinbox(0, 1000, 50, self.duration_var)
        scroll_frame.Label("Pulse Scale (x):")
        scroll_frame.Entry(self.pulse_scale_var)
        scroll_frame.SlideSwitch("Inverted Scroll", self.inverted_scroll_var)

        scroll_frame.AccentButton("Apply Settings", self.apply_settings)
        scroll_frame.AccentButton("Start Smoothed Scroll", self.start_smoothed_scroll)
        scroll_frame.AccentButton("Stop Smoothed Scroll", self.stop_smoothed_scroll)
        scroll_frame.AccentButton("Reset to Default", self.reset_to_default)

    def apply_settings(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            self.stop_smoothed_scroll()

        self.save_config()
        self.start_smoothed_scroll()

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

        smoothed_scroll_config = SmoothedScrollConfig(
            app_config=app_configs
        )

        self.smoothed_scroll_process = multiprocessing.Process(
            target=smoothed_scroll_task,
            args=(smoothed_scroll_config,),
            daemon=True  # Ensure subprocess terminates with the main process
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
            "theme": "sun-valley",
            "mode": "light",
            "scroll_distance": self.distance_var.get(),
            "acceleration": self.acceleration_var.get(),
            "opposite_acceleration": self.opposite_acceleration_var.get(),
            "acceleration_delta": self.acceleration_delta_var.get(),
            "acceleration_max": self.acceleration_max_var.get(),
            "scroll_duration": self.duration_var.get(),
            "pulse_scale": self.pulse_scale_var.get(),
            "inverted_scroll": self.inverted_scroll_var.get()
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

    def on_closing(self):
        self.stop_smoothed_scroll()
        messagebox.showinfo(
            "Smoothed Scroll",
            "Smoothed Scroll is running from the system tray."
        )
        self.root.destroy()

def start_gui_app():
    multiprocessing.freeze_support()
    app = ScrollConfigApp()
    app.root.mainloop()

