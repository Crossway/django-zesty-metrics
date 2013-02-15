import os
from setuptools import setup

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ''

version = '0.1'

setup(
    name='crossway-metrics',
    version=version,
    author='David Eyk',
    author_email='deyk@crossway.org',
    license='BSD',
    packages=['metrics'],
    short_description="Easy stats collection for Django.",
    long_description=long_description,
    install_requires=['statsd>=1.0'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
