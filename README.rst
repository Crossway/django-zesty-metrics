Introduction
============

`django-zesty-metrics` is a middleware suite that uses `statsd` to
report important metrics to a StatD server.

Out of the box, it will track:

* response times individually by view, and in aggregate
* aggregate user activity data


Requirements
============

* Django_ >= 1.4
* statsd_ == 1.0 (StatsD client; `GitHub <https://github.com/jsocol/pystatsd>`)
* `Graphite server`_ (docs_)
* `Statsd server`_ (`blog post`_)


.. _Django: https://pypi.python.org/pypi/Django/
.. _statsd: https://pypi.python.org/pypi/statsd
.. _Graphite server: http://graphite.wikidot.com
.. _docs: https://graphite.readthedocs.org/en/latest/
.. _Statsd server: https://github.com/etsy/statsd
.. _blog post: http://codeascraft.etsy.com/2011/02/15/measure-anything-measure-everything/

Installation
============

To install simply execute `python setup.py install`.


Configuration
=============

In your Django settings:

* Add ``zesty_metrics`` to the ``INSTALLED_APPS``
* Add ``zesty_metrics.middleware.MetricsMiddleware`` to ``MIDDLEWARE_CLASSES``
* Set the following, as needed:
  - ``STATSD_HOST``, default ``localhost``
  - ``STATSD_PORT``, default ``8125``
  - ``STATSD_PREFIX``, default ``None``
* Run ``syncdb`` (or ``migrate`` if you use South).

Set up a cron job to run the ``report_account_stats`` django-admin.py
command regularly. At least once a day, but you can update it as often
as you like.


Acknowledgements
================

Lots of ideas were taken from `django-statsd`_ and `django-munin`_.

.. _django-statsd: https://github.com/WoLpH/django-statsd
.. _django-munin: https://github.com/ccnmtl/django-munin
