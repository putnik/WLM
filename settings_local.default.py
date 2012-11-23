# Local settings for WLM project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Name', 'mail@example.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

GEOIP_PATH = '/usr/share/GeoIP/'

SECRET_KEY = ''

