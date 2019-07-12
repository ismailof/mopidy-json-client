from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-JSON-Client',
    version=get_version('mopidy_json_client/__init__.py'),
    url='https://github.com/ismailof/mopidy-json-client',
    license='Apache License, Version 2.0',
    author='Ismael Asensio',
    author_email='isma.af@gmail.com',
    description='Mopidy Client via JSON/RPC Websocket interface',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'websocket-client',
        'future',
    ],
    entry_points={
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
