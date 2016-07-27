#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
from django.conf import settings
from django.test.runner import DiscoverRunner


os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['zesty_metrics'])
if failures:
    sys.exit(bool(failures))
