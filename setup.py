#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for apns3."""

import setuptools

try:
    README = open('README.rst').read()
    CHANGES = open('CHANGES.rst').read()
except IOError:
    DESCRIPTION = '<placeholder>'
else:
    DESCRIPTION = README + '\n' + CHANGES

setuptools.setup(
    name='apns3',
    version='0.0.0',

    description="A client library for Apple's APNs v3 HTTP/2 push notification service",
    url='https://github.com/joshfriend/apns3',
    author='Josh Friend',
    author_email='josh@fueledbycaffeine.com',

    packages=setuptools.find_packages(),

    long_description=(DESCRIPTION),
    license='MIT',
    classifiers=[
        # TODO: update this list to match your application: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    install_requires=open('requirements/base.txt').readlines(),
    extras_require={
        'pyopenssl': open('requirements/pyopenssl.txt').readlines(),
    }
)
