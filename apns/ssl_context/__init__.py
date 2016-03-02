#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from .stdlib import make_ssl_context  # noqa
except ImportError:  # pragma: no cover
    make_ssl_context = None
try:
    from .openssl import make_ossl_context  # noqa
except ImportError:  # pragma: no cover
    make_ossl_context = None

__all__ = ('make_ssl_context', 'make_ossl_context')
