from __future__ import unicode_literals
from django.apps import AppConfig


class ZestyMetricsConfig(AppConfig):
    name = 'zesty_metrics'

    def ready(self):
        import zesty_metrics.signals
