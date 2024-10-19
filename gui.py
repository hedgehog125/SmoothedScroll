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

def smoothed_scroll_task(config: SmoothedScrollConfig):
    try:
        smoothed_scroll_instance = SmoothedScroll(config=config)
        smoothed_scroll_instance.start(is_block=True)
    except Exception as e:
        print(f"Error in SmoothedScroll process: {e}")

class ScrollConfigApp(TKMT.ThemedTKinterFrame):
    def __init__(self, theme, mode):
        super().__init__("Smoothed Scroll Configuration", theme, mode)
        self.root.iconbitmap("./assets/icon.ico")
        self.distance_var = tk.IntVar(value=120)
        self.acceleration_var = tk.DoubleVar(value=1.0)
        self.opposite_acceleration_var = tk.DoubleVar(value=1.2)
        self.acceleration_delta_var = tk.IntVar(value=70)
        self.acceleration_max_var = tk.IntVar(value=14)
        self.duration_var = tk.IntVar(value=500)
        self.pulse_scale_var = tk.DoubleVar(value=3.0)
        self.inverted_scroll_var = tk.BooleanVar(value=False)
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

    def apply_settings(self):
        print("Applying settings...")
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            print("Smoothed Scroll is running. Restarting with new settings...")
            self.stop_smoothed_scroll()

        self.start_smoothed_scroll()
        print("Settings applied and Smoothed Scroll restarted.")

    def start_smoothed_scroll(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            print("Smoothed Scroll already running.")
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
            daemon=True  
        )
        self.smoothed_scroll_process.start()
        print("Smoothed Scroll started.")

        threading.Thread(target=find_steam_games, daemon=True).start()

    def stop_smoothed_scroll(self):
        if self.smoothed_scroll_process and self.smoothed_scroll_process.is_alive():
            try:
                self.smoothed_scroll_process.terminate()  
                self.smoothed_scroll_process.join(timeout=5)  
                if self.smoothed_scroll_process.is_alive():
                    print("Smoothed Scroll process did not terminate in time.")
                else:
                    print("Smoothed Scroll process terminated.")
            except Exception as e:
                print(f"Error terminating SmoothedScroll process: {e}")
            finally:
                self.smoothed_scroll_process = None
        else:
            print("No Smoothed Scroll process is currently running.")

    def load_disabled_apps(self):

        blocklist_path = './assets/blocklist.json'

        if not os.path.exists(blocklist_path):
            print(f"Blocklist file not found at {blocklist_path}. Using empty blocklist.")
            return []

        try:
            with open(blocklist_path, 'r') as file:
                data = file.read().strip()
                if not data:
                    print("Blocklist JSON file is empty. Using empty blocklist.")
                    return []
                return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error in blocklist file: {e}. Using empty blocklist.")
            return []
        except Exception as e:
            print(f"Unexpected error loading blocklist: {e}. Using empty blocklist.")
            return []

    def on_closing(self):
        print("Closing application...")
        self.stop_smoothed_scroll()
        messagebox.showinfo(
            "Smoothed Scroll",
            "Smoothed Scroll is running from the system tray. Click OK to close the application."
        )
        self.root.destroy()
        print("Application closed.")

def start_gui_app():
    multiprocessing.freeze_support()
    ScrollConfigApp("sun-valley", "light")
