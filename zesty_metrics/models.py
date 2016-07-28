# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError


class LastSeenData(models.Model):
    user = models.OneToOneField(User, db_index=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True,
                                     editable=False,
                                     help_text="Last date this user was active.")
    active_this_month = models.DateTimeField(null=True, db_index=True,
                                             editable=False,
                                             help_text="Was the user active in the past 30 days?")
    active_last_month = models.DateTimeField(null=True, db_index=True,
                                             editable=False,
                                             help_text="Was the user active 30-60 days ago?")

    def update(self, request):
        this_month = datetime.datetime.now() - datetime.timedelta(days=30)
        last_month = datetime.datetime.now() - datetime.timedelta(days=60)
        last_5m = datetime.datetime.now() - datetime.timedelta(minutes=5)
        changed = False

        # We want to know if the user has been active in the previous
        # month (> 30 days).
        if self.active_last_month is None or self.active_last_month <= last_month:
            self.active_last_month = self.active_this_month
            changed = True

        # We want to know the user's most recent time of activity.
        if self.last_seen is None or self.last_seen < last_5m:
            self.last_seen = datetime.datetime.now()
            changed = True

        # We want to know if the user has been active in the past month (< 30 days).
        if self.active_this_month is None or self.active_this_month <= this_month:
            self.active_this_month = self.last_seen
            changed = True

        if changed:
            self.save()


class DailyActivityRecordManager(models.Manager):
    def record_activity(self, who, what):
        try:
            self.create(
                what = what,
                user = who,
            )
        except IntegrityError as e:
            pass


class DailyActivityRecord(models.Model):
    user = models.ForeignKey(User, db_index=True)
    when = models.DateField(auto_now=True, db_index=True,
                            editable=False,
                            help_text="When this user was active.")
    what = models.CharField(max_length=255, db_index=True,
                            unique_for_date='when')

    class Meta:
        unique_together = (
            ('user', 'what', 'when'),
        )

    objects = DailyActivityRecordManager()
