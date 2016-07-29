# -*- coding: utf-8 -*-
from django.conf.urls import include, url


urlpatterns = [
    url(r'^metrics/', include('zesty_metrics.urls')),
]
