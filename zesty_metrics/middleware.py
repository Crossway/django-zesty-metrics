# -*- coding: utf-8 -*-
"""zesty_metrics.middleware -- Timing middleware for StatsD metrics.
"""
from __future__ import with_statement
import time
import threading
import logging

import statsd

from . import models
from . import conf

logger = logging.getLogger('metrics')


class MetricsMiddleware(object):
    """Middleware to capture basic metrics about a request.

    Includes:

    - Performance timing
    - Last-seen data for authenticated users.
    """
    scope = threading.local()

    def __init__(self):
        try:
            self.scope.client = statsd.StatsClient(
                host = conf.HOST,
                port = conf.PORT,
                prefix = conf.PREFIX,
                batch_len = 1000,
                )
        except TypeError:
            # Client doesn't support batch_len, use the default
            self.scope.client = statsd.StatsClient(
                host = conf.HOST,
                port = conf.PORT,
                prefix = conf.PREFIX,
                )

    def process_request(self, request):
        if conf.TIME_RESPONSES:
            self.start_timing(request)
        if conf.TRACK_USER_ACTIVITY:
            self.update_last_seen_data(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if conf.TIME_RESPONSES:
            self.gather_view_data(request, view_func)

    def process_response(self, request, response):
        if conf.TIME_RESPONSES:
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
        method = request.method.lower()
        if request.is_ajax():
            method += '_ajax'
        name = '%s.%s' % (name, method)

        self.scope.view_name = "view." + name

    def stop_timing(self, request):
        """Stop performance timing.
        """
        time_elapsed = time.time() - self.scope.request_start
        client = self.scope.client
        client.timing(
            self.scope.view_name,
            time_elapsed,
            conf.TIMING_SAMPLE_RATE)
        logging.info("Processed %s.%s in %sms",
                      conf.PREFIX, self.scope.view_name, time_elapsed)
        try:
            client.flush()
        except AttributeError:
            # Client doesn't flush, data already sent.
            pass
        logging.info("Flushed stats to %s:%s %s",
                      conf.HOST, conf.PORT, client._addr)

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
