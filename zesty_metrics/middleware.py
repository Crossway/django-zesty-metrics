# -*- coding: utf-8 -*-
import time
import threading
import logging
from uuid import uuid1
from hashlib import md5

from django.core.cache import cache
from django.db import IntegrityError
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin:
        pass

from user_agents import parse as parse_ua
import statsd

from . import models
from . import conf

logger = logging.getLogger('metrics')


request_id_keys = (
    'HTTP_ACCEPT_CHARSET',
    'HTTP_ACCEPT',
    'HTTP_ACCEPT_ENCODING',
    'HTTP_ACCEPT_LANGUAGE',
    'HTTP_CONNECTION',
    'HTTP_USER_AGENT',
    'REMOTE_ADDR',
)


def id_request(request):
    """Generate a uniquish ID for a given request.
    """
    key = '|'.join([
        request.META.get(k, '')
        for k in request_id_keys
    ])
    return md5(uuid1().get_hex() + key).hexdigest()


class LocalStatsd(threading.local):
    def __init__(self):
        client = self.client = statsd.StatsClient(
            host = conf.HOST,
            port = conf.PORT,
            prefix = conf.PREFIX,
        )
        try:
            self.pipeline = client.pipeline()
        except AttributeError:
            # In case we're using an older statsd version.
            self.pipeline = client


class MetricsMiddleware(MiddlewareMixin):
    """Middleware to capture basic metrics about a request.

    Includes:

    - Performance timing
    - Last-seen data for authenticated users.
    """
    scope = LocalStatsd()

    def process_request(self, request):
        request.statsd = self.scope.pipeline
        request.zesty = self.scope
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

        self.scope.id = id_request(request)

        self.scope.agent = parse_ua(request.META.get('HTTP_USER_AGENT', ''))
        self.scope.view_name = "view." + name

    def stop_timing(self, request):
        """Stop performance timing.
        """
        now = time.time()
        started = getattr(self.scope, 'request_start', now)
        time_elapsed = now - started
        if hasattr(self.scope, 'client'):
            client = self.scope.pipeline
            view_name = getattr(self.scope, 'view_name', 'UNKNOWN')
            if time_elapsed:
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
            logger.info("Processed %s.%s in %ss", conf.PREFIX, view_name, time_elapsed)
            try:
                client.send()
            except AttributeError:
                # Client isn't a pipeline, data already sent.
                pass
            except IndexError:
                # Nothing to send.
                pass
            logger.debug("Sent stats to %s:%s", conf.HOST, conf.PORT)
            agent = getattr(self.scope, "agent", None)
            rid = getattr(self.scope, "rid", None)
            if agent and rid:
                data = {
                    'started': started,
                    'server_time': time_elapsed,
                    'agent': agent,
                    'view_name': view_name,
                }
                cache.set('request:' + rid, data, 5 * 60)

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
            except IntegrityError:
                # User probably got created in a concurrent request?
                pass
            except:
                logger.exception("Couldn't update user LastSeenData:")
