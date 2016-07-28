# -*- coding: utf-8 -*-
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core import exceptions
from django.utils.importlib import import_module

import statsd

from zesty_metrics import conf

from zesty_metrics.models import DailyActivityRecord


class Command(BaseCommand):
    help = """Clean up old activity records."""

    option_list = BaseCommand.option_list + (
        make_option('--days', default='90', type=int,
                    help='Delete records older than this many days.'),
    )

    def delete_records(self, delete_before):
        DailyActivityRecord.objects.filter(when__lt=delete_before).delete()


    def handle(self, **options):
        days = options['days']
        today = datetime.date.today()
        delete_before = today - datetime.timedelta(days=days)

        self.delete_records(delete_before)
