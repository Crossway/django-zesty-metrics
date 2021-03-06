# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-27 12:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyActivityRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateField(auto_now=True, db_index=True, help_text=b'When this user was active.')),
                ('what', models.CharField(db_index=True, max_length=255, unique_for_date=b'when')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LastSeenData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_seen', models.DateTimeField(auto_now=True, db_index=True, help_text=b'Last date this user was active.')),
                ('active_this_month', models.DateTimeField(db_index=True, editable=False, help_text=b'Was the user active in the past 30 days?', null=True)),
                ('active_last_month', models.DateTimeField(db_index=True, editable=False, help_text=b'Was the user active 30-60 days ago?', null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='dailyactivityrecord',
            unique_together=set([('user', 'what', 'when')]),
        ),
    ]
