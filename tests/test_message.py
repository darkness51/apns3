#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid
from datetime import datetime, timedelta

import pytest

from apns import Message, Alert, HIGH_PRIORITY, LOW_PRIORITY, \
    EXPIRE_IMMEDIATELY
from apns._compat import binary_type

from tests import EPOCH


class TestMessage(object):

    def test_aps_omits_empty_keys(self):
        m = Message()
        assert m.aps == {}

    def test_aps_with_alert(self):
        a = Alert('Test', 'Message')
        m = Message(alert=a)

        assert m.aps['alert'] == a.payload

    def test_headers_omits_empty_keys(self):
        m = Message(id=None)
        assert 'id' not in m.headers

    def test_headers_encodes_id(self):
        uid = uuid.uuid4()
        m = Message(id=uid)
        assert m.headers['apns-id'] == str(uid)

    def test_headers_encodes_expiration(self):
        m = Message(expiration=EXPIRE_IMMEDIATELY)
        assert m.headers['apns-expiration'] == EXPIRE_IMMEDIATELY
        new_millennium = datetime(2001, 1, 1)
        m = Message(expiration=new_millennium)
        assert m.headers['apns-expiration'] == new_millennium - EPOCH

    @pytest.mark.parametrize('val', [
        1,
        True,
    ])
    def test_set_content_available(self, val):
        m = Message(content_available=val)
        assert m.content_available == 1

    @pytest.mark.parametrize('val', [
        HIGH_PRIORITY,
        LOW_PRIORITY,
    ])
    def test_set_priority(self, val):
        m = Message(priority=val)
        assert m.priority == val

    def test_set_invalid_priority(self):
        with pytest.raises(AssertionError):
            Message(priority=11)

    def test_set_expiration_datetime(self):
        exp = datetime.now().replace(microsecond=0)
        m = Message(expiration=exp)
        assert m.expiration == exp

    def test_set_expiration_unix_timestamp(self):
        m = Message(expiration=1)
        assert m.expiration == EPOCH + timedelta(seconds=1)

    def test_set_expire_immediately(self):
        m = Message(expiration=EXPIRE_IMMEDIATELY)
        assert m.expiration is None
        m = Message(expiration=None)
        assert m.expiration is None

    def test_set_expiration_check_value(self):
        with pytest.raises(AssertionError):
            Message(expiration=-1)

    def test_set_id_with_uuid(self):
        uid = uuid.uuid4()
        m = Message(id=uid)
        assert m.id == uid

    def test_set_id_with_string(self):
        uid = uuid.uuid4()
        m = Message(id=str(uid))
        assert m.id == uid

    def test_payload(self):
        m = Message(alert='test')

        assert 'aps' in m.payload
        aps = m.payload['aps']
        assert aps['alert'] == 'test'

    def test_payload_with_extras(self):
        message = {
            'subject': 'test',
            'body': 'testing',
        }
        m = Message(alert='test', msg=message)

        assert 'aps' in m.payload
        aps = m.payload['aps']
        assert aps['alert'] == 'test'

        assert 'msg' in m.payload
        msg = m.payload['msg']
        assert msg == message

    def test_encode(self):
        m = Message(alert='test')
        enc = m.encoded
        assert type(enc) == binary_type
        # Raises exception if not utf-8 encoded:
        jsondata = enc.decode('utf-8')

        payload = json.loads(jsondata)
        assert payload == m.payload


class TestAlert(object):
    def test_omits_empty_keys(self):
        a = Alert('Test', 'Message', title_loc_key=None)
        assert 'title-loc-key' not in a.payload
