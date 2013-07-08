# -*- coding: utf-8 -*-
"""zesty_metrics.handlers -- user-metrics-related signal handlers.
"""
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in

from statsd import statsd


@receiver(post_save, sender=User)
def handle_new_user(sender, instance, created, **kwargs):
    if created:
        # Increment new usercount
        statsd.incr("users.new")

        # Create LastSeenData object.
        from . import models
        models.LastSeenData.objects.create(user=instance)


@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    statsd.incr("users.login")
