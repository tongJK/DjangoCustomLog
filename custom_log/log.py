import os

import environ

from .logger import get_system_log_message, get_application_log_message

env = environ.Env()

ENABLE_LOGGING = os.environ.get('ENABLE_LOGGING', True)
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO')

REQUEST_ID_HEADER = env.str('REQUEST_ID_HEADER', 'X-Request-ID')

# LOGGING_BACKUPCOUNT = os.environ.get('LOGGING_BACKUPCOUNT', 5)  # (1 current file + 5 backup files)
# LOGGING_MAXBYTES = os.environ.get('LOGGING_MAXBYTES', 1024 * 1024 * 1024)  # File size 1GB


LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s|%(name)s|%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'system': {
            'format': get_system_log_message(),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'application': {
            'format': get_application_log_message(),
            'style': '$',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },

    },
    'filters': {
        'system': {
            '()': 'logger_conicle.filters.CustomRequestIDFilter'
        },
        'ignore_traceback': {
            '()': 'logger_conicle.filters.TracebackInfoFilter'
        },

    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'system_file': {
            'level': LOGGING_LEVEL,
            'filters': ['system', 'ignore_traceback'],
            'class': 'logging.StreamHandler',
            # 'class': 'logging.handlers.RotatingFileHandler',
            # 'filename': settings.LOGGING_FILE_NAME,
            # 'maxBytes': LOGGING_MAXBYTES,
            # 'backupCount': LOGGING_BACKUPCOUNT,
            'formatter': 'system'
        },
        'application_file': {
            'level': 'INFO',
            'filters': ['system', ],
            'class': 'logging.StreamHandler',
            # 'class': 'logging.handlers.RotatingFileHandler',
            # 'filename': settings.LOGGING_FILE_NAME,
            # 'maxBytes': LOGGING_MAXBYTES,
            # 'backupCount': LOGGING_BACKUPCOUNT,
            'formatter': 'application'
        },

    },
    'loggers': {
        'django': {
            'handlers': ['console', 'system_file', ],
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        'application': {
            'handlers': ['application_file', ],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['system_file', ],
            'level': 'INFO',
        },
        'uvicorn': {
            'handlers': ['system_file', ],
            'propagate': False,
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console', ],
        },
    }
}
