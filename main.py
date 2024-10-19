import sys
import signal
import threading
from gui import start_gui_app
from taskbar import start_taskbar_icon

def terminate_processes():
    print("All processes terminated.")

def signal_handler(sig, frame):
    print("Received signal to shut down.")
    terminate_processes()
    sys.exit(0)

def run_gui():
    try:
        start_gui_app()  
    except Exception as e:
        print(f"Error in GUI thread: {e}")

def run_taskbar():
    try:
        start_taskbar_icon()  
    except Exception as e:
        print(f"Error in Taskbar thread: {e}")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler) 

    try:
        gui_thread = threading.Thread(target=run_gui)
        taskbar_thread = threading.Thread(target=run_taskbar)
        print("Starting GUI and Taskbar...")
        gui_thread.start()
        taskbar_thread.start()
        gui_thread.join()
        taskbar_thread.join()
    except KeyboardInterrupt:
        print("Keyboard interrupt received.")
        terminate_processes()
    except Exception as e:
        print(f"Unexpected error: {e}")
        terminate_processes()
    finally:
        terminate_processes()

if __name__ == "__main__":
    main()
