DEBUG = True

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'tests',
    'zesty_metrics',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}


ROOT_URLCONF = 'tests.urls'

ZESTY_TRACKING_CLASSES = (
    'tests.trackers.TestTracker',
    )
