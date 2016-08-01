#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import django
from django.conf import settings
from django.test.runner import DiscoverRunner


os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
django.setup()

test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['zesty_metrics'])
if failures:
    sys.exit(bool(failures))
