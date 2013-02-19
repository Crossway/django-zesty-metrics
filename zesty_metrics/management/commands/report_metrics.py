# -*- coding: utf-8 -*-
"""zesty_metrics.management.commands.report_metrics
"""
import logging

from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.utils.module_loading import import_by_path

from statsd import statsd

from zesty_metrics import conf


class Command(NoArgsCommand):
    help = """Report metrics to StatsD. Run as a cron job for maximum effect."""

    try:
        statsd = statsd.StatsClient(
            host = conf.HOST,
            port = conf.PORT,
            prefix = conf.PREFIX,
            batch_len = 1000)
    except TypeError:
        # Client doesn't support batch_len
        statsd = statsd.statsd

    def track(self, tracker, kind, func):
        for attr, name in getattr(tracker, kind, {}).iteritems():
            try:
                value = getattr(tracker, attr)
                if callable(value):
                    value = value()
            except:
                logging.error("%s::%s: NO VALUE", kind, name)
            else:
                logging.info("%s::%s: %s", kind, name, value)
                func(name, value)

    def handle_noargs(self, **options):
        trackers = [import_by_path(tracker) for tracker in conf.TRACKING_CLASSES]

        for tracker in trackers:
            tracker = tracker()
            self.track(tracker, 'gauges', statsd.gauge)
            self.track(tracker, 'counters', statsd.incr)

        self.statsd.flush()
