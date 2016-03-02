# APNS3

[![Build Status](https://travis-ci.org/joshfriend/apns3.svg?branch=master)](https://travis-ci.org/joshfriend/apns3)
[![Coverage Status](https://coveralls.io/repos/github/joshfriend/apns3/badge.svg?branch=develop)](https://coveralls.io/github/joshfriend/apns3?branch=develop)

A client library for Apple's APNS v3 HTTP/2 push notification service

## Requirements
Python which supports TLSv1.2 is required. This means that only Python 2
version 2.7.11 and higher and Python 3 version 3.4.0 and higher are supported
unless you use pyOpenSSL.

To install with pyOpenSSL support:

```
pip install apns3[pyopenssl]
```
