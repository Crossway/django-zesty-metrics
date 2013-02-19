# -*- coding: utf-8 -*-
"""zesty_metrics.conf -- configuration values
"""
import statsd
from django.conf import settings
from . import defaults

HOST = statsd.host
PORT = statsd.port
PREFIX = statsd.prefix
TIME_RESPONSES = getattr(settings, 'ZESTY_TIME_RESPONSES',
                         defaults.ZESTY_TIME_RESPONSES)

TIMING_SAMPLE_RATE = getattr(settings, 'ZESTY_TIMING_SAMPLE_RATE',
                             defaults.ZESTY_TIMING_SAMPLE_RATE)
TRACKING_CLASSES = getattr(settings, 'ZESTY_TRACKING_CLASSES',
                           defaults.ZESTY_METRICS_CLASSES)

TRACK_USER_ACTIVITY = getattr(settings, 'ZESTY_TRACK_USER_ACTIVITY',
                              defaults.ZESTY_TRACK_USER_ACTIVITY)
