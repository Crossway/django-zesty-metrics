# -*- coding: utf-8 -*-
"""zesty_metrics.management.commands.report_metrics
"""
import logging

from django.core.management.base import NoArgsCommand
from django.core import exceptions
from django.utils.importlib import import_module

import statsd

from zesty_metrics import conf


class Command(NoArgsCommand):
    help = """Report metrics to StatsD. Run as a cron job for maximum effect."""

    try:
        statsd = statsd.StatsClient(
            host = conf.HOST,
            port = conf.PORT,
            prefix = conf.PREFIX,
            batch_len = 1000,
            )
    except TypeError:
        # Client doesn't support batch_len
        statsd = statsd.StatsClient(
            host = conf.HOST,
            port = conf.PORT,
            prefix = conf.PREFIX,
            )

    def _track(self, tracker, kind, func):
        """Track items on a tracker. Internal helper method.
        """
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

    def _import_tracker(self, path):
        """"Import and instantiate a tracker from the given dotted path.
        """
        try:
            module, classname = path.rsplit('.', 1)
        except ValueError:
            raise exceptions.ImproperlyConfigured('%s isn\'t a tracker module' % path)
        try:
            mod = import_module(module)
        except ImportError, e:
            raise exceptions.ImproperlyConfigured('Error importing tracker %s: "%s"' % (module, e))
        try:
            klass = getattr(mod, classname)
        except AttributeError:
            raise exceptions.ImproperlyConfigured('Tracker module "%s" does not define a "%s" class' % (module, classname))
        return klass()

    def handle_noargs(self, **options):
        trackers = [self._import_tracker(tp) for tp in conf.TRACKING_CLASSES]

        for tracker in trackers:
            self._track(tracker, 'gauges', self.statsd.gauge)
            self._track(tracker, 'counters', self.statsd.incr)

        try:
            self.statsd.flush()
        except AttributeError:
            # Client doesn't flush, data already sent.
            pass
