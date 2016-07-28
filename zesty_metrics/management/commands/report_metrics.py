# -*- coding: utf-8 -*-
import logging

from django.core.management.base import NoArgsCommand
from django.core import exceptions
from importlib import import_module

import statsd

from zesty_metrics import conf


class Command(NoArgsCommand):
    help = """Report metrics to StatsD. Run as a cron job for maximum effect."""

    statsd = statsd.StatsClient(
        host = conf.HOST,
        port = conf.PORT,
        prefix = conf.PREFIX,
        )

    try:
        pipeline = statsd.pipeline()
    except AttributeError:
        # statsd < 2.0
        pipeline = statsd

    def _track(self, tracker, kind, func):
        """Track items on a tracker. Internal helper method.
        """
        for attr, name in getattr(tracker, kind, {}).iteritems():
            try:
                value = getattr(tracker, attr)
                if callable(value):
                    value = value()
            except:
                logging.error("%s::%s.%s: NO VALUE", kind, conf.PREFIX, name)
            else:
                logging.info("%s::%s.%s: %s", kind, conf.PREFIX, name, value)
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
            self._track(tracker, 'gauges', self.pipeline.gauge)
            self._track(tracker, 'counters', self.pipeline.incr)

        try:
            self.pipeline.send()
        except AttributeError:
            # Client doesn't flush, data already sent.
            pass
        except IndexError:
            # Nothing in the pipeline to send.
            pass
