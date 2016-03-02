#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

import pytest
from mock import Mock

from apns import Client, Message, DEFAULT_PORT, ALTERNATE_PORT
from apns.client import APNS_SANDBOX_HOST, APNS_PRODUCTION_HOST
from apns.exceptions import BadDeviceToken, Unregistered


class TestAPNSClient(object):
    @pytest.mark.parametrize('port', [
        DEFAULT_PORT,
        ALTERNATE_PORT,
    ])
    def test_check_port_number(self, port):
        try:
            Client(None, port=port)
        except AssertionError:
            pytest.fail('Valid port was rejected')

    def test_bad_port(self):
        with pytest.raises(AssertionError):
            Client(None, port=80)

    @pytest.mark.parametrize('host,is_sandbox', [
        (APNS_SANDBOX_HOST, True),
        (APNS_PRODUCTION_HOST, False),
    ])
    def test_get_host(self, host, is_sandbox):
        client = Client(None, sandbox=is_sandbox)
        assert client.host == host

    @pytest.mark.parametrize('token', [
        '',
        None,
    ])
    def test_push_checks_null_or_empty_token(self, token):
        c = Client(None)
        with pytest.raises(AssertionError):
            c.push('message', token)

    def test_push(self):
        id_ = uuid.uuid4()
        res = Mock()
        res.status = 200
        res.headers = {
            'apns-id': [str(id_)],
        }

        con = Mock()
        con.get_response.return_value = res

        c = Client(None)
        c._connection = con

        m = Message(alert='testing')

        apns_id = c.push(m, 'token')
        assert apns_id == id_

        args, kwargs = con.request.call_args
        assert args[0] == 'POST'
        assert args[1] == '/3/device/token'
        assert kwargs['body'] == m.encoded
        assert kwargs['headers'] == m.headers

    def test_push_not_successful(self):
        res = Mock()
        res.status = 400
        res.read.return_value = b'{"reason": "BadDeviceToken"}'
        res.headers = {
            'apns-id': [str(uuid.uuid4())],
        }

        con = Mock()
        con.get_response.return_value = res

        c = Client(None)
        c._connection = con

        m = Message(alert='testing')

        try:
            c.push(m, 'token')
            pytest.fail('Did not raise BadDeviceToken')
        except BadDeviceToken as e:
            assert e.token == 'token'
            assert e.code == res.status

    @pytest.mark.parametrize('exc_cls,data', [
        (BadDeviceToken, b'{"reason": "BadDeviceToken"}'),
        (Unregistered, b'{"reason": "Unregistered", "timestamp": 0}'),
    ])
    def test_handle_error(self, exc_cls, data):
        response = Mock()
        response.read.return_value = data
        response.status = 400

        c = Client(None)
        try:
            c.handle_error('asdf', response)
            pytest.fail('Did not raise `%s`' % exc_cls.__name__)
        except exc_cls as e:
            assert e.code == 400
            assert e.token == 'asdf'

    def test_handle_unknown_error(self):
        response = Mock()
        response.read.return_value = b'{"reason": "ABCD1234"}'

        c = Client(None)
        try:
            c.handle_error('asdf', response)
            pytest.fail('Did not raise an Exception')
        except Exception as e:
            assert type(e) == Exception
