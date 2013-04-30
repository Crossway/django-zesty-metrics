import json
from django.http import HttpResponse
from django.views.generic.edit import ProcessFormView, FormMixin

import statsd

from . import conf
from . import forms


class StatView(ProcessFormView, FormMixin):
    http_method_names = ['post']
    stat_method = None

    def get_client(self):
        try:
            return statsd.StatsClient(
                host = conf.HOST,
                port = conf.PORT,
                prefix = conf.PREFIX,
                batch_len = 1000,
                )
        except TypeError:
            # Client doesn't support batch_len, use the default
            return statsd.StatsClient(
                host = conf.HOST,
                port = conf.PORT,
                prefix = conf.PREFIX,
                )

    def form_valid(self, form):
        self.send_stat(form)
        return HttpResponse(status=204)

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors), status=400)

    def send_stat(self, form):
        client = self.get_client()
        handler = getattr(client, self.stat_method)
        handler(self.kwargs['stat'], **form.cleaned_data)


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
