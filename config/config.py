import logging
import os.path


# Secrets
YT_API_KEY = ""
YT_CHANNEL_ID = ""
VK_API_KEY = ""
VK_OWNER_ID = ""

#
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CONFIG_DIR)
FILE_LAST_ID = os.path.join(BASE_DIR, 'last_id')
FILE_LOG = os.path.join(BASE_DIR, 'logs', 'log')

# Logging
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': logging.BASIC_FORMAT,
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'level': 'NOTSET',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'NOTSET',
            'formatter': 'standard',
            'filename': FILE_LOG,
        },
    },
    'loggers': {
        'yt2vk': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
        },
    },
}

