Introduction
============

`crossway-metrics` is a middleware suite that uses `statsd` to log query
and view durations to statsd.

* Statsd Client
    - https://github.com/jsocol/pystatsd
* Graphite
    - http://graphite.wikidot.com
* Statsd
    - code: https://github.com/etsy/statsd
    - blog post: http://codeascraft.etsy.com/2011/02/15/measure-anything-measure-everything/


Install
=======

To install simply execute `python setup.py install`.


Configuration
=============

In

* Just add `metrics` to the `INSTALLED_APPS`
* Add `metrics.middleware.MetricsMiddleware` to `MIDDLEWARE_CLASSES`
* Set the following, as needed:
  - `STATSD_HOST`, default `localhost`
  - `STATSD_PORT`, default `8125`
  - `STATSD_PREFIX`, default `None`
