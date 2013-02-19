# -*- coding: utf-8 -*-
"""zesty_metrics.tracking -- tracking metrics for user accounts.
"""
import datetime as dt
from functools import wraps

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Q

from . import models


def cache_metric(func_or_expiration):
    """Metric caching decorator.

    Usage::

        class PhilosophyTracker(Tracker):
            @property
            @Tracker.cache_metric(58 * 60)  # 58 minutes
            def life_universe_everything(self):
                return 42
    """
    def decorator(func):
        if isinstance(int, func_or_expiration):
            expiration = func_or_expiration
        else:
            expiration = 5 * 60  # 5 minutes

        key = 'zesty_metric_%s' % func.__name__

        @wraps(func)
        def wrapper(self):
            result = cache.get(key, None)
            if result is None:
                result = func(self)
                cache.set(key, result, expiration)
            return result

        return wrapper

    if callable(func_or_expiration):
        return decorator(func_or_expiration)
    else:
        return decorator


class Tracker(object):
    gauges = {}
    counters = {}

    cache_metric = staticmethod(cache_metric)


class UserAccounts(Tracker):
    # Map metrics object attributes to gauge names:
    gauges = dict(
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
    @cache_metric
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
    @cache_metric
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
    @cache_metric
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
    @cache_metric
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
    @cache_metric
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
    @cache_metric
    def churned_users_count(self):
        """Count of users who showed up 30-60 days ago who have not shown up in the past 30 days.
        """
        return self.churned_users.count()

    @property
    @cache_metric
    def retention_rate(self):
        """The percentage of users who showed up last month who also showed up this month.
        """
        try:
            return float(self.returning_users_count) / self.last_month_users_count
        except ZeroDivisionError:
            return 0.0

    @property
    @cache_metric
    def churn_rate(self):
        """1 - retention rate; the percentage of users who showed up last month who did not show up this month.
        """
        return 1 - self.retention_rate

    @property
    @cache_metric
    def user_duration_average(self):
        """Defined as 1 / churn; the number of months the average customer attends.
        """
        try:
            return 1 / self.churn_rate
        except ZeroDivisionError:
            return 0.0

    @property
    @cache_metric
    def engagement_ratio(self):
        """How good are we at driving retention?
        """
        try:
            return self.daily_active_users_count / float(self.monthly_active_users_count)
        except ZeroDivisionError:
            return 0.0
