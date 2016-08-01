DEBUG = True

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'tests',
    'zesty_metrics.apps.ZestyMetricsConfig',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]


ROOT_URLCONF = 'tests.urls'

ZESTY_TRACKING_CLASSES = [
    'tests.trackers.TestTracker',
]
