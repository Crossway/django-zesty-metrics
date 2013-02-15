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


Usage
=====

Just add `metrics` to the `INSTALLED_APPS` and add
`metrics.middleware.TimingMiddleware` to `MIDDLEWARE_CLASSES`


Advanced Usage
--------------

    >>> def some_view(request):
    ...     with request.statsd.timer('something_to_time'):
    ...         # do something here
    ...         pass
    >>>
    >>> def some_view(request):
    ...     start = time.time()
    ...     # do something here
    ...     request.statsd.timing('something_to_time', time.time() - start)

