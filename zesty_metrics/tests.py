# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.test.client import Client
from django.test import TestCase

from django.core.cache import cache
from django.contrib.auth.models import User

from mock import Mock, patch, call

import six

import statsd
from user_agents import parse as parse_ua

from zesty_metrics import middleware
from zesty_metrics import views
from zesty_metrics import models
from zesty_metrics.management.commands import cleanup
from zesty_metrics.management.commands import report_metrics

TOMORROW = date.today() + timedelta(days=1)


def patch_today(todays_date):
    class FakeDateType(type):
        def __instancecheck__(self, instance):
            return isinstance(instance, date)

    class FakeDate(six.with_metaclass(FakeDateType, date)):
        @classmethod
        def today(cls):
            return todays_date

    return patch('datetime.date', FakeDate)


class ClientTestCase(TestCase):
    def setUp(self):
        self.username = 'fred'
        self.password = 's3kr1t'
        self.user = User.objects.create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.unauthed_client = Client()
        super(ClientTestCase, self).setUp()


class ActivityTests(ClientTestCase):
    def test_GET_should_return_a_transparent_png(self):
        response = self.client.get('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, views.TRANSPARENT_1X1_PNG)

    def test_GET_should_store_activity(self):
        response = self.client.get('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 200)
        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)
        event = activity[0]
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.what, 'foo')

    def test_subsequent_GET_should_NOT_store_activity_on_the_same_day(self):
        # Event 1
        response = self.client.get('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 200)
        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)
        # Event 2
        response = self.client.get('/metrics/activity/foo/')
        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)

    def test_subsequent_GET_should_store_activity_on_a_new_day(self):
        # Event 1
        response = self.client.get('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 200)
        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)
        # Event 2
        with patch_today(TOMORROW):
            response = self.client.get('/metrics/activity/foo/')
            self.assertEqual(response.status_code, 200)

        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 2)

    def test_POST_should_return_an_empty_204(self):
        response = self.client.post('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')

    def test_POST_should_store_activity(self):
        response = self.client.post('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 204)

        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)
        event = activity[0]
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.what, 'foo')
        self.assertEqual(event.when, date.today())

    def test_subsequent_POST_should_NOT_store_activity_on_the_same_day(self):
        # Event 1
        response = self.client.post('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 204)
        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)
        # Event 2
        response = self.client.post('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 204)
        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)

    def test_subsequent_POST_should_store_activity_on_a_new_day(self):
        # Event 1
        response = self.client.post('/metrics/activity/foo/')
        self.assertEqual(response.status_code, 204)
        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 1)
        # Event 2
        with patch_today(TOMORROW):
            response = self.client.post('/metrics/activity/foo/')
            self.assertEqual(response.status_code, 204)

        activity = models.DailyActivityRecord.objects.all()
        self.assertEqual(activity.count(), 2)


class MockedStatsdTestCase(ClientTestCase):
    def setUp(self):
        self.original_pipeline = middleware.MetricsMiddleware.scope.pipeline
        self.patched_pipeline = middleware.MetricsMiddleware.scope.pipeline = Mock()
        self.patched_StatsClient = Mock()
        self.original_StatsClient = statsd.StatsClient
        statsd.StatsClient = lambda *a, **k: self.patched_StatsClient
        super(MockedStatsdTestCase, self).setUp()

    def tearDown(self):
        middleware.MetricsMiddleware.scope.pipeline = self.original_pipeline
        statsd.StatsClient = self.original_StatsClient
        super(MockedStatsdTestCase, self).tearDown()


class IncrViewTests(MockedStatsdTestCase):
    method = 'incr'
    stat_name = 'foo'
    required_data = {}
    default_data = {'count': 1, 'rate': 1.0}
    optional_data = {'count': 2, 'rate': 2.0}

    def get_url(self):
        return '/metrics/%s/%s/' % (self.method, self.stat_name)

    def test_GET_should_return_a_transparent_png(self):
        response = self.client.get(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, views.TRANSPARENT_1X1_PNG)

    def test_GET_should_send_a_stat(self):
        response = self.client.get(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 200)
        handler = getattr(self.patched_StatsClient, self.method)
        expected_data = self.default_data.copy()
        expected_data.update(self.required_data)
        handler.assert_called_once_with(
            self.stat_name,
            **expected_data
        )

    def test_GET_should_send_a_stat_with_args(self):
        data = self.required_data.copy()
        data.update(self.optional_data)
        response = self.client.get(self.get_url(), data=data)
        self.assertEqual(response.status_code, 200)
        handler = getattr(self.patched_StatsClient, self.method)
        handler.assert_called_once_with(
            self.stat_name,
            **data
        )

    def test_POST_should_return_an_empty_204(self):
        response = self.client.post(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')

    def test_POST_should_send_a_stat(self):
        response = self.client.post(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 204)
        handler = getattr(self.patched_StatsClient, self.method)
        expected_data = self.default_data.copy()
        expected_data.update(self.required_data)
        handler.assert_called_once_with(
            self.stat_name,
            **expected_data
        )

    def test_POST_should_send_a_stat_with_args(self):
        data = self.required_data.copy()
        data.update(self.optional_data)
        response = self.client.post(self.get_url(), data=data)
        self.assertEqual(response.status_code, 204)
        handler = getattr(self.patched_StatsClient, self.method)
        handler.assert_called_once_with(
            self.stat_name,
            **data
        )


class DecrViewTests(IncrViewTests):
    method = 'decr'
    stat_name = 'foo'
    default_data = {'count': 1, 'rate': 1.0}
    optional_data = {'count': 2, 'rate': 2.0}


class TimingViewTests(IncrViewTests):
    method = 'timing'
    stat_name = 'foo'
    default_data = {}
    required_data = {'delta': 1}
    optional_data = required_data


class GaugeViewTests(IncrViewTests):
    method = 'gauge'
    stat_name = 'foo'
    default_data = {'delta': False}
    required_data = {'value': 1}
    optional_data = {'delta': True}


CHROME_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'


class ReportRequestRenderedViewTests(MockedStatsdTestCase):
    method = 'timing'
    request_id = 'foo'
    default_data = {}
    required_data = {'delta': 1}
    optional_data = required_data

    def setUp(self):
        super(ReportRequestRenderedViewTests, self).setUp()
        cache_key = 'request:%s' % self.request_id
        data = {
            'started': 5000,
            'server_time': 150,
            'agent': parse_ua(CHROME_UA),
            'view_name': 'bar',
        }
        cache.set(cache_key, data)

    def get_url(self):
        return '/metrics/report-request-rendered/%s/' % (self.request_id)

    def test_GET_should_return_a_transparent_png(self):
        response = self.client.get(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, views.TRANSPARENT_1X1_PNG)

    def test_GET_should_send_a_stat(self):
        with patch('time.time', return_value=5500):
            response = self.client.get(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 200)
        handler = getattr(self.patched_StatsClient, self.method)
        handler.assert_has_calls([
            call(
                'bar',
                delta = 500,
            ),
            call(
                'bar.Chrome',
                delta = 500,
            ),
            call(
                'browsers.Chrome',
                delta = 500,
            ),
        ])

    def test_POST_should_return_an_empty_204(self):
        response = self.client.post(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')

    def test_POST_should_send_a_stat(self):
        with patch('time.time', return_value=5500):
            response = self.client.post(self.get_url(), data=self.required_data)
        self.assertEqual(response.status_code, 204)
        handler = getattr(self.patched_StatsClient, self.method)
        expected_data = self.default_data.copy()
        expected_data.update(self.required_data)
        handler.assert_has_calls([
            call(
                'bar',
                delta = 500,
            ),
            call(
                'bar.Chrome',
                delta = 500,
            ),
            call(
                'browsers.Chrome',
                delta = 500,
            ),
        ])


class CleanupCommandTests(ClientTestCase):
    def setUp(self):
        super(CleanupCommandTests, self).setUp()
        for days in range(1, 99, 10):
            fake_today = date.today() - timedelta(days=days)
            with patch_today(fake_today):
                models.DailyActivityRecord.objects.create(
                    what = 'foo',
                    user = self.user,
                )

    def tearDown(self):
        super(CleanupCommandTests, self).tearDown()
        models.DailyActivityRecord.objects.all().delete()

    def test_it_should_clean_up_old_activity_records(self):
        activities = models.DailyActivityRecord.objects.all()
        self.assertEqual(activities.count(), 10)

        cleaner = cleanup.Command()
        cleaner.handle(days=30)

        self.assertEqual(activities.count(), 3)


class ReportMetricsCommandTests(TestCase):
    def test_it_should_report_metrics_from_the_configured_test_tracker(self):
        reporter = report_metrics.Command()

        pipeline_p = 'zesty_metrics.management.commands.report_metrics.Command.pipeline'
        with patch(pipeline_p) as patched:
            reporter.handle()

            patched.gauge.assert_has_calls([
                call(
                    'things.foo',
                    5,
                ),
            ])

            patched.incr.assert_has_calls([
                call(
                    'stuff.bar',
                    20,
                ),
            ])
