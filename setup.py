import os
from setuptools import setup

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ''

version = '0.1'

setup(
    name='django-zesty-metrics',
    version=version,
    author='David Eyk',
    author_email='deyk@crossway.org',
    url='https://github.com/Crossway/django-zesty-metrics',
    license='BSD',
    packages=['zesty_metrics'],
    description="Zesty metrics collection and Statsd integration for Django.",
    long_description=long_description,
    install_requires=['statsd>=1.0', 'Django>=1.4'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
