# -*- coding: utf-8 -*-
"""metrics.tracking -- tracking metrics for user accounts.
"""
import datetime as dt

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Q

from . import models


def _cache_metric(func):
    key = 'metric_%s' % func.__name__

    def get_metric(self):
        result = cache.get(key, None)
        if result is None:
            result = func(self)
            cache.set(key, result, 58 * 60)  # 58 minutes
        return result

    return get_metric


class _Metrics(object):
    @property
    def past_day(self):
        return dt.datetime.now() - dt.date.resolution

    @property
    def past_30_days(self):
        return dt.datetime.now() - (dt.date.resolution * 30)

    @property
    def past_60_days(self):
        return dt.datetime.now() - (dt.date.resolution * 60)

    @property
    def daily_active_users(self):
        """Query for users active in the past day.
        """
        return models.LastSeenData.objects.filter(last_seen__gte=self.past_day)

    @property
    @_cache_metric
    def daily_active_users_count(self):
        """Count of users active in the past day.
        """
        return self.daily_active_users.count()

    @property
    def monthly_active_users(self):
        """Query for users active in the past 30 days.
        """
        return models.LastSeenData.objects.filter(last_seen__gte=self.past_30_days)

    @property
    @_cache_metric
    def monthly_active_users_count(self):
        """Count of users active in the past 30 days.
        """
        return self.monthly_active_users.count()

    @property
    def new_users(self):
        """Query of newly registered users in the past 30 days.
        """
        return User.objects.filter(date_joined__gte=self.past_30_days)

    @property
    @_cache_metric
    def new_users_count(self):
        """Count of newly registered users in the past 30 days.
        """
        return self.new_users.count()

    @property
    def last_month_users(self):
        """Query for users who showed up last month.
        """
        return models.LastSeenData.objects.filter(
            (Q(last_seen__gte=self.past_60_days) \
             | Q(active_this_month__gte=self.past_60_days) \
             | Q(active_last_month__gte=self.past_60_days))
            & (Q(last_seen__lt=self.past_30_days) \
               | Q(active_this_month__lt=self.past_30_days) \
               | Q(active_last_month__lt=self.past_30_days))
            )

    @property
    @_cache_metric
    def last_month_users_count(self):
        """Count of users who showed up 30-60 days ago.
        """
        return self.last_month_users.count()

    @property
    def returning_users(self):
        """Query for users who showed up 30-60 days ago who also showed up in the past 30 days.
        """
        return self.last_month_users.filter(
            last_seen__gte=self.past_30_days
            )

    @property
    @_cache_metric
    def returning_users_count(self):
        """Count of users who showed up 30-60 days ago who also showed up in the past 30 days.
        """
        return self.returning_users.count()

    @property
    def churned_users(self):
        """Query for users who showed up 30-60 days ago who have not shown up in the past 30 days.
        """
        return self.last_month_users.filter(
            last_seen__lte=self.past_30_days,
            )

    @property
    @_cache_metric
    def churned_users_count(self):
        """Count of users who showed up 30-60 days ago who have not shown up in the past 30 days.
        """
        return self.churned_users.count()

    @property
    @_cache_metric
    def retention_rate(self):
        """The percentage of users who showed up last month who also showed up this month.
        """
        try:
            return float(self.returning_users_count) / self.last_month_users_count
        except ZeroDivisionError:
            return 0.0

    @property
    @_cache_metric
    def churn_rate(self):
        """1 - retention rate; the percentage of users who showed up last month who did not show up this month.
        """
        return 1 - self.retention_rate

    @property
    @_cache_metric
    def user_duration_average(self):
        """Defined as 1 / churn; the number of months the average customer attends.
        """
        try:
            return 1 / self.churn_rate
        except ZeroDivisionError:
            return 0.0

    @property
    @_cache_metric
    def engagement_ratio(self):
        """How good are we at driving retention?
        """
        try:
            return self.daily_active_users_count / float(self.monthly_active_users_count)
        except ZeroDivisionError:
            return 0.0


metrics = _Metrics()
