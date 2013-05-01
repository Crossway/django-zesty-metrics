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
        client = self.scope.client = statsd.StatsClient(
            host = conf.HOST,
            port = conf.PORT,
            prefix = conf.PREFIX,
            )
        try:
            self.scope.pipeline = client.pipeline()
        except AttributeError:
            # In case we're using an older statsd version.
            self.scope.pipeline = client

    def process_request(self, request):
        try:
            if conf.TIME_RESPONSES:
                self.start_timing(request)
        except:
            logger.exception('Exception occurred while logging to statsd.')

    def process_exception(self, request, exception):
        try:
            if hasattr(self.scope, 'client'):
                self.scope.pipeline.incr('view.exceptions')
                view_name = (getattr(self.scope, 'view_name', 'UNKNOWN') +
                             '.exceptions')
                self.scope.pipeline.incr(view_name)
        except:
            logger.exception('Exception occurred while logging to statsd.')

    def process_view(self, request, view_func, view_args, view_kwargs):
        if conf.TIME_RESPONSES:
            self.gather_view_data(request, view_func)

    def process_response(self, request, response):
        if conf.TRACK_USER_ACTIVITY:
            self.update_last_seen_data(request)
        if conf.TIME_RESPONSES:
            try:
                self.stop_timing(request)
            except:
                logger.exception('Exception occurred while logging to statsd.')

        return response

    def start_timing(self, request):
        """Start performance timing.
        """
        self.scope.request_start = time.time()
        request.statsd = self.scope.pipeline

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
        now = time.time()
        time_elapsed = now - getattr(self.scope, 'request_start', now)
        if hasattr(self.scope, 'client'):
            client = self.scope.pipeline
            view_name = getattr(self.scope, 'view_name', 'UNKNOWN')
            client.timing(
                view_name,
                time_elapsed,
                conf.TIMING_SAMPLE_RATE)
            client.timing(
                'view.aggregate-response-time',
                time_elapsed,
                conf.TIMING_SAMPLE_RATE)
            client.incr(view_name + '.requests')
            client.incr('view.requests')
            logger.info("Processed %s.%s in %ss",
                          conf.PREFIX, view_name, time_elapsed)
            try:
                client.send()
            except AttributeError:
                # Client isn't a pipeline, data already sent.
                pass
            logger.debug("Sent stats to %s:%s",
                          conf.HOST, conf.PORT)

    # Other visit data
    def update_last_seen_data(self, request):
        """Update the user's LastSeenData profile.
        """
        try:
            user = request.user
        except AttributeError:
            # No user, so nothing to do here.
            return

        if user.is_authenticated():
            try:
                data = models.LastSeenData.objects.get(user=user)
            except models.LastSeenData.DoesNotExist:
                data = models.LastSeenData(user=user)
            try:
                data.update(request)
            except:
                logger.exception("Couldn't update user LastSeenData:")
