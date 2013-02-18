# -*- coding: utf-8 -*-
"""metrics.models -- user-metrics-related models.
"""
from django.db import models
from django.contrib.auth.models import User


class LastSeenData(models.Model):
    user = models.ForeignKey(User, unique=True, db_index=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True,
                                     editable=False,
                                     help_text="Last date this user was active.")
    active_this_month = models.DateTimeField(null=True, db_index=True,
                                             editable=False,
                                             help_text="Was the user active in the past 30 days?")
    active_last_month = models.DateTimeField(null=True, db_index=True,
                                             editable=False,
                                             help_text="Was the user active 30-60 days ago?")
