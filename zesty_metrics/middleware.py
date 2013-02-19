# -*- coding: utf-8 -*-
"""zesty_metrics.middleware -- Timing middleware for StatsD metrics.
"""
from __future__ import with_statement
import datetime
import time
import threading
import logging

from django.conf import settings

import statsd

from . import models

logger = logging.getLogger('metrics')


class MetricsMiddleware(object):
    """Middleware to capture basic metrics about a request.

    Includes:

    - Performance timing
    - Last-seen data for authenticated users.
    """
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
            batch_len = 100,
        )

    def process_request(self, request):
        self.start_timing(request)
        self.handle_last_seen_data(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.gather_view_data(request, view_func)

    def process_response(self, request, response):
        self.stop_timing(request)
        return response

    def start_timing(self, request):
        """Start performance timing.
        """
        self.scope.request_start = time.time()
        request.statsd = self.scope.client

    def gather_view_data(self, request, view_func):
        """Discover the view name.
        """
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

    def stop_timing(self, request):
        """Stop performance timing.
        """
        time_elapsed = time.time() - self.scope.request_start
        client = self.scope.client
        client.timing(
            self.scope.view_name,
            time_elapsed,
            self.TIMING_SAMPLE_RATE)
        logging.debug("Processed %s.%s in %sms",
                      self.PREFIX, self.scope.view_name, time_elapsed)
        client.flush()
        logging.debug("Flushed stats to %s:%s %s",
                      self.HOST, self.PORT, client._addr)

    # Other visit data
    def update_last_seen_data(self, request):
        """Update the user's LastSeenData profile.
        """
        user = request.user
        if user.is_authenticated():
            try:
                data = models.LastSeenData.objects.get(user=user)
            except models.SiteProfile.DoesNotExist:
                data = models.LastSeenData(user=user)
            data.update(request)
