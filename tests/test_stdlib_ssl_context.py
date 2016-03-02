#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ssl

import pytest
from mock import patch, Mock

from apns import make_ssl_context


class TestStdlibSSLContext(object):
    def test_require_tls1_2(self):
        with pytest.raises(AssertionError):
            make_ssl_context('cert.pem', 'key.pem',
                             protocol=ssl.PROTOCOL_TLSv1_1)

    @patch('apns.ssl_context.stdlib.ssl')
    def test_make_context_sets_apln_npn_protocols(self, mock_ssl):
        mock_ssl.PROTOCOL_TLSv1_2 = 1
        ctx_mock = Mock()
        mock_ssl.SSLContext.return_value = ctx_mock
        ctx = make_ssl_context('cert.pem', 'key.pem')

        assert ctx is ctx_mock
        args, _ = ctx.set_alpn_protocols.call_args
        alpn_protos = args[0]
        assert 'h2' in alpn_protos
        args, _ = ctx.set_npn_protocols.call_args
        npn_protos = args[0]
        assert 'h2' in npn_protos
