from config.common_settings import *

DEBUG = True
SECRET_KEY = 'some secret'

INSTALLED_APPS += [
    'debug_toolbar',
]

DATABASES['default'].update({
    'NAME': 'mymdb',
    'USER': 'mymdb',
    'PASSWORD': 'development',
    'HOST': 'localhost',
    'PORT': '5433',
})

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default-locmemcache',
        'TIMEOUT': 5,
    }
}
MEDIA_ROOT = os.path.join(BASE_DIR, '../media_root')

INTERNAL_IPS = [
    '127.0.0.1',
]