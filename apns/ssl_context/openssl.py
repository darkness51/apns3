#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Wrapper for OpenSSL context that includes the wrap_socket method:
from hyper.ssl_compat import SSLContext
from hyper.tls import H2_NPN_PROTOCOLS
from OpenSSL import SSL
from OpenSSL.crypto import load_certificate, load_privatekey, FILETYPE_PEM

__all__ = ('make_ossl_context')


def make_ossl_context(certstring=None, keystring=None, certfile=None,
                      keyfile=None, password=None, method=SSL.TLSv1_2_METHOD,
                      options=SSL.OP_ALL):
    """make_ossl_context(certstring=None, keystring=None, certfile=None, \
                         keyfile=None, password=None,                    \
                         method=OpenSSL.SSL.TLSv1_2_METHOD,              \
                         options=OpenSSL.SSL.OP_ALL)

    Create a PyOpenSSL SSL context from an APNs SSL certificate. You can use
    this if your version of Python does not support TLSv1.2. You should use
    this only if you cannot use :func:`make_ssl_context`.

    :param certificate: Path to the certificate file. Must be in PEM format.
    :param keyfile: Path to the private key file. Must be in PEM format.
    :param password: Optional password to decrypt the private key.
    :param protocol: The Channel encryption protocol to use when connecting to
        the APNs gateway.
    :param options: Options to set on the context.
    :return: A :class:`hyper.ssl_compat.SSLContext`. This class wraps
        :class:`OpenSSL.SSL.Context` to provide an interface resembling
        :class:`ssl.SSLContext`. Use this when creating a :class:`.Client`.
    """

    assert method >= SSL.TLSv1_2_METHOD, 'TLSv1.2 or higher is required'

    context = SSLContext(method)
    context.options = options
    context.set_npn_protocols(H2_NPN_PROTOCOLS)
    context.set_alpn_protocols(H2_NPN_PROTOCOLS)

    if certfile and keyfile:
        context.load_cert_chain(
            certfile,
            keyfile=keyfile,
            password=password
        )
    elif certstring and keystring:
        cert = load_certificate(FILETYPE_PEM, certstring)
        key = load_privatekey(FILETYPE_PEM, keystring, passphrase=password)
        # Context wrapper doesn't expose these methods
        context._ctx.use_certificate(cert)
        context._ctx.use_privatekey(key)
    else:
        raise ValueError(
            'Certificate and key are required, but were not provided'
        )

    return context
