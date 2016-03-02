#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exception hierarchy::

    APNSException
     +-- RequestError
     |    +-- PayloadError
     |    |    +-- PayloadEmpty
     |    |    +-- PayloadTooLarge
     |    +-- HeaderError
     |    |    +-- BadMessageId
     |    |    +-- BadExpirationDate
     |    |    +-- BadPriority
     |    |    +-- TokenError
     |    |    |    +-- BadDeviceToken
     |    |    |    +-- DeviceTokenNotForTopic
     |    |    |    +-- Unregistered
     |    |    +-- TopicError
     |    |    |    +-- BadTopic
     |    |    |    +-- TopicDisallowed
     |    |    |    +-- MissingTopic
     +-- CertificateError
     |    +-- BadCertificateEnvironment
     |    +-- BadCertificate
     +-- HTTPError
     |    +-- TooManyRequests
     |    +-- IdleTimeout
     |    +-- InternalServerError
     |    +-- Forbidden

These exceptions (excluding the base class exceptions) map to values of the
`reason field <https://developer.apple.com/library/ios/documentation/Networking
Internet/Conceptual/RemoteNotificationsPG/Chapters/APNsProviderAPI.html#//apple
_ref/doc/uid/TP40008194-CH101-SW5>`_ that is returned by the APNs gateway in
event of an error. Some values of the ``reason`` key do not have an associated
exception because this library includes checks to prevent these errors.
 """

import sys
import inspect
from datetime import datetime

from ._compat import iteritems


class APNSException(Exception):
    """Base exception class for all APNs exceptions."""

    description = 'A error occurred sending the APNS notification'

    def __init__(self, code, *args):
        Exception.__init__(self)

        #: The HTTP status code of the response that raised this error
        self.code = code

    def __str__(self):
        return self.description


class RequestError(APNSException):
    """Base exception class for errors related to the APNs request headers or
    data payload.
    """

    description = 'There was a problem with the request.'


class PayloadError(RequestError):
    """Raised if there was invalid information in the request payload"""

    description = 'The was an error with the request payload.'


class PayloadEmpty(PayloadError):
    """Raised if no payload was sent to the gateway."""

    description = 'The message payload was empty.'


class PayloadTooLarge(PayloadError):
    """Raised if the payload size exceeds 4kb."""

    description = (
        'The message payload was too large. The maximum payload size is 4096 '
        'bytes.'
    )


class HeaderError(RequestError):
    """Base exception class for errors related to request headers."""

    description = 'There was a problem with one of the request headers.'


class BadMessageId(HeaderError):
    """Raised if the :attr:`~apns.message.Message.id` assigned by the user is
    not a valid UUID.
    """

    description = 'The `apns-id` header is bad.'


class BadExpirationDate(HeaderError):
    """Raised if the provided message expiration date is invalid."""

    description = 'The `apns-expiration` header is bad.'


class BadPriority(HeaderError):
    """Raised if the message priority value is invalid."""

    description = 'The `apns-priority` value is bad.'


class TokenError(HeaderError):
    """Base exception class for errors related to the APNs token."""

    description = 'There was a problem with the device token.'

    def __init__(self, code, token, *args):
        HeaderError.__init__(self, code)

        #: The token of the device that raised this error
        self.token = token


class BadDeviceToken(TokenError):
    """Raised if the provided token has an invalid format, or if the token is
    linked to the wrong certificate environment.
    """

    description = (
        'The specified device token was bad. Verify that the request contains '
        'a valid token and that the token matches the environment.'
    )


class DeviceTokenNotForTopic(TokenError):
    """Raised if the token does not match the specified topic."""

    description = 'The device token does not match the specified topic.'


class Unregistered(TokenError):
    """Raised if the device token is valid, but is no longer registered to
    receive push notifications for the given topic.
    """

    description = 'The device token is inactive for the specified topic.'

    def __init__(self, code, token, ts):
        TokenError.__init__(self, code, token)

        #: The last time at which APNs confirmed that the device token was no
        #: longer valid for the topic. Stop pushing notifications until the
        #: device registers a token with a later timestamp with your provider.
        self.unavailable_since = datetime.utcfromtimestamp(ts)


class TopicError(HeaderError):
    """Base exception class for errors related to the APNs topic."""

    description = 'There was an issue with the `apns-topic` header.'


class BadTopic(TopicError):
    """Raised if the message topic is not in the certificate you create in
    Member Center.
    """

    description = 'The `apns-topic` header was invalid.'


class TopicDisallowed(TopicError):
    """Raised if pushing to the provided topic is not allowed."""

    description = 'Pushing to this topic is not allowed.'


class MissingTopic(TopicError):
    """Raised if the message is missing a topic when the topic is required. A
    topic is always required when the certificate supports multiple topics.
    """

    description = (
        'The `apns-topic` header of the request was not specified and was '
        'required. The `apns-topic` header is mandatory when the client is '
        'connected using a certificate that supports multiple topics.'
    )


class CertificateError(APNSException):
    """Base exception class for errors related to the SSL certificate."""

    description = 'There was a problem with the client certificate.'


class BadCertificateEnvironment(CertificateError):
    """Raised if the SSL certificate used was not created for the environment
    that the push is sent to. This can happen if you try to send a push message
    to the sandbox gateway using the production gateway certificate.
    """

    description = 'The client certificate was for the wrong environment.'


class BadCertificate(CertificateError):
    """Raised if the certificate is invalid (possibly expired)."""

    description = 'The certificate was bad.'


class HTTPError(APNSException):
    """Base exception class for request errors not related to the APNs data
    payload.
    """

    description = 'There was a problem with the HTTP request to APNS.'


class Forbidden(HTTPError):
    """*403* `Forbidden`"""

    description = 'The specified action is not allowed.'


class TooManyRequests(HTTPError):
    """*429* `TOO MANY REQUESTS`

    Raised if too many requests were made consecutively to the same device
    token.
    """
    description = (
        'Too many requests were made consecutively to the same device token.'
    )


class IdleTimeout(HTTPError):
    description = 'Idle time out.'


class InternalServerError(HTTPError):
    """*500* `INTERNAL SERVER ERROR`

    Raised if there was an error with the APNs service."""

    description = 'An internal server error occurred.'


__classes = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))
_map = {k: v for k, v in iteritems(__classes) if v.__module__ == __name__}
del __classes
__all__ = tuple(_map.keys())
