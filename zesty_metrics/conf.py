# -*- coding: utf-8 -*-
"""zesty_metrics.conf -- configuration values
"""
import statsd
from django.conf import settings
from . import defaults

HOST = statsd.host,
PORT = statsd.port,
PREFIX = statsd.prefix,
TIMING_SAMPLE_RATE = getattr(settings, 'ZESTY_TIMING_SAMPLE_RATE',
                             defaults.ZESTY_TIMING_SAMPLE_RATE)
TRACKING_CLASSES = getattr(settings, 'ZESTY_TRACKING_CLASSES',
                           defaults.ZESTY_METRICS_CLASSES)
