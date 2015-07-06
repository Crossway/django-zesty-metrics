from zesty_metrics.tracking import Tracker


class TestTracker(Tracker):
    # Map metrics object attributes to gauge names:
    gauges = dict(
        foo = 'things.foo',
    )
    counters = dict(
        bar = 'stuff.bar',
    )

    @property
    def foo(self):
        return 5

    @property
    def bar(self):
        return 20
