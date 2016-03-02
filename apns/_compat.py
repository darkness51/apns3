#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

PY2 = sys.version_info[0] == 2


if PY2:
    iterkeys = lambda x: x.iterkeys()
    itervalues = lambda x: x.itervalues()
    iteritems = lambda x: x.iteritems()
    binary_type = str
    text_type = unicode  # noqa
else:
    iterkeys = lambda x: x.keys()
    itervalues = lambda x: x.value()
    iteritems = lambda x: x.items()
    binary_type = bytes
    text_type = str

_missing = object()


class cached_property(property):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::
        class Foo(object):
            @cached_property
            def foo(self):
                # calculate something important here
                return 42
    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: A subclass of python's builtin property
    # decorator, we override __get__ to check for a cached value. If one
    # choses to invoke __get__ by hand the property will still work as
    # expected because the lookup logic is replicated in __get__ for
    # manual invocation.

    # Taken from Werkzeug
    # http://werkzeug.pocoo.org/

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
