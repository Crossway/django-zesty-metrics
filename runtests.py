#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
from django.conf import settings

try:
    # Django <= 1.8
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
except ImportError:
    # Django >= 1.8
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['zesty_metrics'])
if failures:
    sys.exit(bool(failures))
