import psutil
import time
import os
from .write_blocklist import write_blocklist

def find_steam_games():
    while True: 
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                if "steam" in proc.info['name'].lower() and "steamwebhelper" not in proc.info['name'].lower() and proc.info['exe']:
                    parent = psutil.Process(proc.info['pid'])
                    children = parent.children(recursive=True)
                    for child in children:
                        if child.exe() and "steamwebhelper" not in child.name().lower():
                            exe_name = os.path.splitext(os.path.basename(child.exe()))[0]
                            write_blocklist(exe_name + '.exe')
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        time.sleep(5)
