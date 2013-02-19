# -*- coding: utf-8 -*-
"""zesty_metrics.management.commands.report_account_stats -- script for reporting account stats.
"""
import logging

from django.core.management.base import NoArgsCommand

from statsd import statsd

from metrics import tracking


class Command(NoArgsCommand):
    help = "Report accounts stats to StatsD."

    # Map metrics object attributes to gauge names:
    attr_gauge = dict(
        new_users_count = 'users.new_this_month',
        daily_active_users_count = 'users.active.daily',
        monthly_active_users_count = 'users.active.monthly',
        last_month_users_count = 'users.active.last_month',
        returning_users_count = 'users.active.returning_this_month',
        churned_users_count = 'users.churned',
        retention_rate = 'users.retention_rate',
        churn_rate = 'users.churn_rate',
        user_duration_average = 'users.average_duration',
        engagement_ratio = 'users.engagement_ratio',
        )

    def handle_noargs(self, **options):
        for attr, gauge in self.attr_gauge.iteritems():
            try:
                value = getattr(tracking.metrics, attr)
            except:
                logging.error("%s: NO VALUE")
            else:
                logging.info("%s: %s", gauge, value)
                statsd.gauge(gauge, value)
