import os
import json

def write_blocklist(process):
    file_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'SmoothedScroll', 'blacklist.json')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # print(file_path)
    blocklist = []
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                blocklist = json.load(file)
            except json.JSONDecodeError:
                pass
    
    if process not in blocklist:
        blocklist.append(process)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(blocklist, file, indent=2)