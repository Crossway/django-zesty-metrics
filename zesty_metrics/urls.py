from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = patterns('',
                       url(r'^incr/(?P<stat>[^/]+)/?',
                           csrf_exempt(views.IncrView.as_view()),
                           name="metrics_incr"),
                       url(r'^decr/(?P<stat>[^/]+)/?',
                           csrf_exempt(views.DecrView.as_view()),
                           name="metrics_decr"),
                       url(r'^timing/(?P<stat>[^/]+)/?',
                           csrf_exempt(views.TimingView.as_view()),
                           name="metrics_timing"),
                       url(r'^gauge/(?P<stat>[^/]+)/?',
                           csrf_exempt(views.GaugeView.as_view()),
                           name="metrics_gauge"),
                       url(r'^report-request-rendered/(?P<request_id>[^/]+)/?',
                           csrf_exempt(views.RequestTimingReportView.as_view()),
                           name="metrics_report_request_rendered")
                       )
