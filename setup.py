import os
from setuptools import setup, find_packages

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ''

version = '0.5'

setup(
    name='django-zesty-metrics',
    version=version,
    author='David Eyk',
    author_email='deyk@crossway.org',
    url='https://github.com/Crossway/django-zesty-metrics',
    license='BSD',
    packages=find_packages(),
    description="Zesty metrics collection and Statsd integration for Django.",
    long_description=long_description,
    install_requires=[
        'Django>=1.9',
        'pyyaml==5.1',
        'six',
        'statsd==2.1.2',
        'ua-parser==0.3.5',
        'user-agents==0.2.0',
    ],

    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
