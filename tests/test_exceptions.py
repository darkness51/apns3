#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apns.exceptions import Unregistered

from tests import EPOCH


class TestExceptions(object):
    def test_unregistered_timestamp(self):
        e = Unregistered(400, 'asdf', 0)

        assert e.code == 400
        assert e.token == 'asdf'
        assert e.unavailable_since == EPOCH
