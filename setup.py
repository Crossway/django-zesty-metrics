import os
from setuptools import setup

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ''

version = '0.3.1'

setup(
    name='django-zesty-metrics',
    version=version,
    author='David Eyk',
    author_email='deyk@crossway.org',
    url='https://github.com/Crossway/django-zesty-metrics',
    license='BSD',
    packages=['zesty_metrics', 'zesty_metrics.management', 'zesty_metrics.migrations'],
    description="Zesty metrics collection and Statsd integration for Django.",
    long_description=long_description,
    install_requires=['statsd==2.1.2', 'Django>=1.4',
                      'pyyaml==3.11', 'ua-parser==0.3.5', 'user-agents==0.2.0'],

    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
