# -*- coding: utf-8 -*-
"""zesty_metrics.forms -- various data-handling forms.
"""
from django import forms


class DefaultIntegerField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        self.default = kwargs.pop('default', None)
        super(DefaultIntegerField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        result = super(DefaultIntegerField, self).to_python(value)
        if result is None:
            result = self.default
        return result


class DefaultFloatField(forms.FloatField):
    def __init__(self, *args, **kwargs):
        self.default = kwargs.pop('default', None)
        super(DefaultFloatField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        result = super(DefaultFloatField, self).to_python(value)
        if result is None:
            result = self.default
        return result


class ActivityForm(forms.Form):
    pass



class CountForm(forms.Form):
    rate = DefaultFloatField(required=False,
                             default=1.0,
                             help_text="Sample rate, between 0 and 1.")
    count = DefaultIntegerField(default=1, required=False)



class TimingForm(forms.Form):
    delta = forms.IntegerField(required=True)


class GaugeForm(forms.Form):
    value = forms.FloatField(required=True)
    delta = forms.BooleanField(required=False)
