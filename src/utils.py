import os
import sys

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

ICON = resource_path("icon.ico")
MESSAGE_DT = 5
MAX_WAIT_TIME = 60
XPATH_SEND_MESSAGE_FIELD = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div/p'
ADDITIONAL_TOOLS_FIELD = '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div[2]/div/div/div/span'
ATTACHMENTS_BUTTON = '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div[2]/button'
MEDIA_XPATH = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
DOCS_XPATH  = '//input[@accept="*"]'
SEND_MEDIA_XPATH = '//*[@id="app"]/div/div[3]/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div'
MESSAGE_SEPARATOR = '[break]'
FILE_SEPARATOR = '[file]'
QUEUE_SEPARATOR = '[queue]'
WINDOWS_SIZE = "1080x720"
bg_color = "#26657b"
button_color = "#ffb444"
border_color = "#e69500"
hover_color = "#ff9800"