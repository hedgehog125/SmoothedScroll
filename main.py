import json
import easing_functions
from win32con import VK_SHIFT
from SmoothedScroll import (SmoothedScroll, SmoothedScrollConfig, AppConfig, ScrollConfig)
from utils.steam_blocklist import find_steam_games

find_steam_games()

def load_disabled_apps(filename='./assets/blocklist.json'):
    with open(filename, 'r') as file:
        return json.load(file)

if __name__ == '__main__':
    disabled_apps = load_disabled_apps()
    app_configs = [
        AppConfig(
            regexp=r'.*',
            scroll_config=ScrollConfig(
                distance=None,  # [px] None - automatic detection by the system (default=120)
                acceleration=1.,  # [x] scroll down acceleration
                opposite_acceleration=1.2,  # [x] scroll up acceleration
                acceleration_delta=70,  # [ms]
                acceleration_max=14,  # [x] max acceleration steps
                duration=500,  # [ms]
                pulse_scale=3,  # [x] tail to head ratio
                ease=easing_functions.LinearInOut,  # Easing function
                inverted=False,  # down, up = up, down
                horizontal_scroll_key=VK_SHIFT  # VK_SHIFT, VK_CONTROL, VK_MENU
            ),
        ),
    ]
    for app in disabled_apps:
        app_configs.append(AppConfig(
            regexp=r'.*' + app,
            enabled=False
        ))
    SmoothedScroll(
        config=SmoothedScrollConfig(
            app_config=app_configs
        )
    ).start(is_block=True)
