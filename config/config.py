import os.path


# Secrets
YT_API_KEY = ""
VK_API_KEY = ""
YT_CHANNEL_ID = ""
VK_OWNER_ID = ""

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CONFIG_DIR)
FILE_LAST_ID = os.path.join(BASE_DIR, 'last_id')

