from pystray import Icon, MenuItem, Menu
from PIL import Image

def on_quit(icon, item):
    icon.stop()

def on_show_message(icon, item):
    icon.notify("Это уведомление из системного трея!")

image_path = './assets/icon.ico'  
image = Image.open(image_path)

menu = Menu(
    MenuItem('Показать сообщение', on_show_message),
    MenuItem('Выход', on_quit)
)

icon = Icon("test", image, "Smoothed Scroll", menu)
icon.run()
