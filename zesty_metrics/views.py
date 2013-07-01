# -*- coding: utf-8 -*-
"""zesty_metrics.views -- metrics reporting views
"""
import time
import json
from django.http import HttpResponse
from django.views.generic.edit import ProcessFormView, FormMixin
from django.forms import Form
from django.core.cache import cache

import statsd

from . import conf
from . import forms


TRANSPARENT_1X1_PNG = \
("\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52"
 "\x00\x00\x00\x01\x00\x00\x00\x01\x08\x03\x00\x00\x00\x28\xcb\x34"
 "\xbb\x00\x00\x00\x19\x74\x45\x58\x74\x53\x6f\x66\x74\x77\x61\x72"
 "\x65\x00\x41\x64\x6f\x62\x65\x20\x49\x6d\x61\x67\x65\x52\x65\x61"
 "\x64\x79\x71\xc9\x65\x3c\x00\x00\x00\x06\x50\x4c\x54\x45\x00\x00"
 "\x00\x00\x00\x00\xa5\x67\xb9\xcf\x00\x00\x00\x01\x74\x52\x4e\x53"
 "\x00\x40\xe6\xd8\x66\x00\x00\x00\x0c\x49\x44\x41\x54\x78\xda\x62"
 "\x60\x00\x08\x30\x00\x00\x02\x00\x01\x4f\x6d\x59\xe1\x00\x00\x00"
 "\x00\x49\x45\x4e\x44\xae\x42\x60\x82\x00")


class StatView(ProcessFormView, FormMixin):
    http_method_names = ['get', 'post']
    stat_method = None

    def get_client(self):
        try:
            return self.request.statsd
        except AttributeError:
            # We must not be using the Middleware.
            return statsd.StatsClient(
                host = conf.HOST,
                port = conf.PORT,
                prefix = conf.PREFIX,
                )

    def form_valid(self, form):
        self.send_stat(form)
        if self.request.method == 'POST':
            return HttpResponse(status=204)
        else:
            return HttpResponse(TRANSPARENT_1X1_PNG, mimetype="image/png")

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors), status=400)

    def get_stat_data(self, form):
        return {self.kwargs['stat']: form.cleaned_data}

    def send_stat(self, form):
        client = self.get_client()
        handler = getattr(client, self.stat_method)
        stat_data = self.get_stat_data()
        if stat_data is not None:
            for name, value in stat_data.iteritems():
                handler(name, **data)


class IncrView(StatView):
    """Increment a counter.
    """
    form_class = forms.IncrForm
    stat_method = 'incr'


class DecrView(IncrView):
    """Decrement a counter.
    """
    stat_method = 'decr'


class TimingView(StatView):
    """Record timing data.
    """
    form_class = forms.TimingForm
    stat_method = 'timing'


class GaugeView(StatView):
    """Set a gauge value.
    """
    form_class = forms.GaugeForm
    stat_method = 'gauge'


class RequestTimingReportView(TimingView):
    form_class = Form
    stat_method = 'timing'

    def get_stat_data(self):
        now = time.time()
        self.request_id = self.kwargs['request_id']
        cache_key = 'request:' + self.request_id
        data = cache.get(cache_key, None)
        if data is not None:
            cache.delete(cache_key, None)
            delta = now - data.get('started', now)
            agent = data.get('agent', None)
            if agent is not None:
                payload = {'delta': delta}
                names = [
                    "{ua.browser.family}",
                    "{ua.browser.family} {ua.browser.version_string}",
                    "{ua.browser.family} {ua.browser.version_string} {ua.os.family} {ua.os.version_string}".format(ua=agent),
                ]
                for name in names:
                    print '#'*15, name, payload
                return dict((name, payload) for name in names)
