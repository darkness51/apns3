#!/usr/bin/env python
# -*- coding: utf-8 -*-

from OpenSSL import SSL
from OpenSSL.crypto import FILETYPE_PEM

import pytest
from mock import patch, Mock

from apns import make_ossl_context


class TestOpenSSLContext(object):
    def test_require_tls1_2(self):
        with pytest.raises(AssertionError):
            make_ossl_context(
                certfile='cert.pem',
                keyfile='key.pem',
                method=SSL.TLSv1_1_METHOD
            )

    def test_require_cert_files_or_strings(self):
        with pytest.raises(ValueError):
            make_ossl_context()

    @patch('apns.ssl_context.openssl.SSLContext')
    def test_make_context_sets_apln_npn_protocols(self, mock_context):
        ctx = make_ossl_context(certfile='cert.pem', keyfile='key.pem')

        args, _ = ctx.set_alpn_protocols.call_args
        alpn_protos = args[0]
        assert 'h2' in alpn_protos
        args, _ = ctx.set_npn_protocols.call_args
        npn_protos = args[0]
        assert 'h2' in npn_protos

    @patch('apns.ssl_context.openssl.SSLContext', Mock())
    @patch('apns.ssl_context.openssl.load_privatekey')
    @patch('apns.ssl_context.openssl.load_certificate')
    def test_load_from_strings(self, load_certificate, load_privatekey):
        mock_cert = Mock()
        load_certificate.return_value = mock_cert
        mock_key = Mock()
        load_privatekey.return_value = mock_key

        wrapper = make_ossl_context(
            certstring='certificate',
            keystring='privatekey',
            password='password'
        )

        args, _ = load_certificate.call_args
        assert args == (FILETYPE_PEM, 'certificate')
        args, kwargs = load_privatekey.call_args
        assert args == (FILETYPE_PEM, 'privatekey')
        assert kwargs['passphrase'] == 'password'

        ctx = wrapper._ctx
        args, _ = ctx.use_certificate.call_args
        assert args[0] is mock_cert
        args, _ = ctx.use_privatekey.call_args
        assert args[0] is mock_key
