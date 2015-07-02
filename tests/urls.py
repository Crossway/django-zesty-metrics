# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^metrics/', include('zesty_metrics.urls')),
)
