#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from uuid import UUID

from hyper import HTTP20Connection

from ._compat import binary_type
from .exceptions import _map

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__all__ = ('Client',)

#: The hostname for the APNs sandbox gateway server.
APNS_SANDBOX_HOST = 'api.development.push.apple.com'

#: The hostname for the APNs production gateway server.
APNS_PRODUCTION_HOST = 'api.push.apple.com'

#: This is the default port to use when connecting to APNs.
DEFAULT_PORT = 443

#: An alternate port which can be used when connecting to APNs if the default
#: port is blocked for some reason.
ALTERNATE_PORT = 2197


class Client(object):
    """Object representing a connection to an APNS gateway server.

    :param ssl_context: The SSL context to use to connect to the APNS gateway.
        Use either :func:`make_ssl_context` or :func:`make_ossl_context` to
        create this context.
    :param sandbox: (optional) Whether or not to use the APNS sandbox as the
        gateway server. Defaults to the sandbox server.
    :param port: (optional) The port to use when connecting to the gateway.
        Defaults to :data:`.DEFAULT_PORT` (443), but may also be
        :data:`.ALTERNATE_PORT` (2197).
    """
    def __init__(self, ssl_context, sandbox=True, port=DEFAULT_PORT):
        self.sandbox = sandbox

        assert port in (DEFAULT_PORT, ALTERNATE_PORT), 'Invalid port number'
        self._port = port

        self._connection = HTTP20Connection(
            self.host,
            port=self.port,
            ssl_context=ssl_context
        )

    @property
    def port(self):
        """The APNS gateway server connection port number."""
        return self._port

    @property
    def host(self):
        """The APNS gateway server hostname."""
        return [APNS_PRODUCTION_HOST, APNS_SANDBOX_HOST][self.sandbox]

    def push(self, message, token):
        """Send a message to a device.


        :param message: A :class:`.Message` object.
        :param token: Device token to push the message to.
        :return: A :class:`~uuid.UUID` that identifies the notification. This
            will be the same as :attr:`.Message.id` if you provided and ID for
            the message. If no ID was provided, the APNs server will create one
            for you.
        :raises: :class:`.APNSException` if the push was not
            successful.
        """
        assert token, 'Token cannot be empty or null'

        path = '/3/device/' + token
        stream_id = self._connection.request(
            'POST',
            path,
            body=message.encoded,
            headers=message.headers
        )

        response = self._connection.get_response(stream_id)
        if response.status != 200:
            self.handle_error(token, response)

        apns_id = response.headers['apns-id'][0]
        if isinstance(apns_id, binary_type):
            apns_id = apns_id.decode('utf-8')
        return UUID(apns_id)

    def handle_error(self, token, response):
        data = json.loads(response.read().decode('utf-8'))
        reason = data.get('reason', None)
        timestamp = data.get('timestamp', None)
        exc = _map.get(reason, None)
        if exc:
            raise exc(response.status, token, timestamp)
        else:
            raise Exception(reason)
