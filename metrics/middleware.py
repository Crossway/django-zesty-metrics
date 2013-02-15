# -*- coding: utf-8 -*-
"""metrics.middleware -- Timing middleware for StatsD metrics.
"""
from __future__ import with_statement
import time
import threading

from django.conf import settings

import statsd


class TimingMiddleware(object):
    scope = threading.local()

    HOST = getattr(settings, 'STATSD_HOST', 'localhost')
    PORT = getattr(settings, 'STATSD_PORT', 8125)
    PREFIX = getattr(settings, 'STATSD_PREFIX', None)
    TIMING_SAMPLE_RATE = getattr(settings, 'STATSD_TIMING_SAMPLE_RATE', 1)

    def __init__(self):
        self.scope.client = statsd.StatsClient(
            host = self.HOST,
            port = self.PORT,
            prefix = self.PREFIX,
            batch_len = 10,
            )

    def process_request(self, request):
        self.scope.request_start = time.time()
        request.statsd = self.scope.client

    def process_view(self, request, view_func, view_args, view_kwargs):
        # View name is defined as module.view
        # (e.g. django.contrib.auth.views.login)
        name = view_func.__module__

        # CBV specific
        if hasattr(view_func, '__name__'):
            name = '%s.%s' % (name, view_func.__name__)
        elif hasattr(view_func, '__class__'):
            name = '%s.%s' % (name, view_func.__class__.__name__)
        if request.is_ajax():
            name += '_ajax'

        self.scope.view_name = "view." + name

    def process_response(self, request, response):
        client = self.scope.client
        client.timing(
            self.scope.view_name,
            time.time() - self.scope.request_start,
            self.TIMING_SAMPLE_RATE)
        client.flush()
