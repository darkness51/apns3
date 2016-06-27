#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid
from datetime import datetime

from ._compat import iteritems, binary_type, cached_property

__all__ = ('Alert', 'Message', 'HIGH_PRIORITY', 'LOW_PRIORITY',
           'EXPIRE_IMMEDIATELY')

_EPOCH = datetime(1970, 1, 1)

#: Send the push message immediately. Notifications with this priority must
#: trigger an alert, sound, or badge on the target device. It is an error
#: to use this priority for a push notification that contains only the
#: ``content-available`` key.
HIGH_PRIORITY = '10'

#: Send the push message at a time that takes into account power
#: considerations for the device. Notifications with this priority might be
#: grouped and delivered in bursts. They are throttled, and in some cases
#: are not delivered.
LOW_PRIORITY = '5'

#: If the message expiration is ``0``, APNs treats the notification as if
#: it expires immediately and does not store the notification or attempt to
#: redeliver it.
EXPIRE_IMMEDIATELY = 0


class Message(object):
    """
    An APNs message.

    :param id: A canonical :class:`~uuid.UUID` that identifies the
        notification. If there is an error sending the notification, APNs uses
        this value to identify the notification to your server. You may pass a
        :class:`~uuid.UUID` object, or any value which can be used to create
        one. If you omit this value, a new :class:`~uuid.UUID` is created by
        APNs and returned by :meth:`Client.push`.
    :param priority: The priority of the notification. Can be either
        :data:`.HIGH_PRIORITY` or :data:`.LOW_PRIORITY`.
    :param expiration: A UNIX epoch date expressed in seconds (UTC), or a
        :class:`~datetime.datetime`. This identifies the date when the
        notification is no longer valid and can be discarded. If this value is
        nonzero, APNs stores the notification and tries to deliver it at least
        once, repeating the attempt as needed if it is unable to deliver the
        notification the first time. If the value is 0 or ``None``, APNs treats
        the notification as if it expires immediately and does not store the
        notification or attempt to redeliver it.
    :param alert: If this property is included, the system displays a standard
        alert or a banner, based on the user’s OS settings. You can specify a
        string or an :class:`.Alert` as the value of ``alert``. If you specify
        a string, it becomes the message text of an alert with two buttons:
        Close and View. If the user taps View, the app launches. If you specify
        an :class:`.Alert`, more complex behavior is supported. See the
        documentation for :class:`.Alert` for details.
    :param badge: The number to display as the badge of the app icon. If this
        property is absent, the badge is not changed. To remove the badge, set
        the value of this property to ``0``.
    :param topic: The topic of the remote notification, which is typically the
        bundle ID for your app. The certificate you create in Member Center
        must include the capability for this topic. If your certificate
        includes multiple topics, you must specify a value for this attribute.
        If you omit this value and your APNs certificate does not specify
        multiple topics, the APNs server uses the certificate’s Subject as the
        default topic.
    :param category: Provide this key with a string value that represents the
        identifier property of the ``UIMutableUserNotificationCategory`` object
        you created to define custom actions. To learn more about using custom
        actions, see `Registering Your Actionable Notification Types`_.
    :param sound: The name of a sound file in the app bundle or in the
        ``Library/Sounds`` folder of the app’s data container. The sound in
        this file is played as an alert. If the sound file doesn’t exist or
        default is specified as the value, the default alert sound is played.
        The audio must be in one of the audio data formats that are compatible
        with system sounds; see `Preparing Custom Alert Sounds`_ for details.
    :param content_available: Provide this key with a value of ``True`` to
        indicate that new content is available. Including this key and value
        means that when your app is launched in the background or resumed,
        ``application:didReceiveRemoteNotification:fetchCompletionHandler:``
        is called.
    :param extra: Extra information to bundle with the notification payload.

    .. _Registering Your Actionable Notification Types: https://developer.apple
        .com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNoti
        ficationsPG/Chapters/IPhoneOSClientImp.html#//apple_ref/doc/uid/TP40008
        194-CH103-SW26
    .. _Preparing Custom Alert Sounds: https://developer.apple.com/library/ios/
        documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapt
        ers/IPhoneOSClientImp.html#//apple_ref/doc/uid/TP40008194-CH103-SW6
    """
    def __init__(self, id=None, topic=None, alert=None, badge=None,
                 sound=None, category=None, content_available=None,
                 expiration=EXPIRE_IMMEDIATELY, priority=HIGH_PRIORITY,
                 **extra):
        #: A canonical :class:`~uuid.UUID` that identifies the notification.
        self.id = id

        #: The priority of the notification.
        self.priority = priority

        #: A :class:`~datetime.datetime` representing when the notification is
        #: no longer valid and can be discarded.
        self.expiration = expiration

        #: The Alert to show in the app.
        self.alert = alert

        #: The number to display as the badge of the app icon.
        self.badge = badge

        #: The topic of the remote notification
        self.topic = topic

        #: The notification category
        self.category = category

        #: The notification sound to play when the message is received.
        self.sound = sound

        #: Indicates that new content is available.
        self.content_available = content_available

        #: Extra information to bundle with the notification payload.
        self.extra = extra

    @property
    def aps(self):
        """The content of the ``aps`` dictionary."""
        if isinstance(self.alert, Alert):
            alert = self.alert.payload
        else:
            alert = self.alert

        aps = {
            'alert': alert,
            'badge': self.badge,
            'sound': self.sound,
            'content-available': self.content_available,
            'category': self.category,
        }
        aps = {k: v for k, v in iteritems(aps) if v is not None}
        return aps

    @property
    def content_available(self):
        return self._content_available

    @content_available.setter
    def content_available(self, value):
        # This key should be 1 if "true" and omitted if "false"
        self._content_available = None
        if value:
            self._content_available = 1

    @cached_property
    def headers(self):
        _id = None
        if self.id:
            _id = str(self.id)

        _exp = EXPIRE_IMMEDIATELY
        if self.expiration:
            _exp = self.expiration - _EPOCH

        hdrs = {
            'apns-id': _id,
            'apns-topic': self.topic,
            'apns-priority': self.priority,
            'apns-expiration': str(_exp),
        }
        return {k: v for k, v in iteritems(hdrs) if v is not None}

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, uuid.UUID):
            # Raises ValueError if UUID string is invalid
            value = uuid.UUID(value)
        self._id = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        assert value in (LOW_PRIORITY, HIGH_PRIORITY), 'Invalid priority'
        self._priority = value

    @property
    def expiration(self):
        if not self._expiration:
            return None
        return datetime.utcfromtimestamp(self._expiration)

    @expiration.setter
    def expiration(self, value):
        if isinstance(value, datetime):
            diff = value - _EPOCH
            value = diff.total_seconds()
        if value:
            assert value >= 0, 'Invalid expiration'
        self._expiration = value

    @cached_property
    def payload(self):
        """The payload data of the message. See `the Remote Notification
        Payload <https://developer.apple.com/library/ios/documentation/Networki
        ngInternet/Conceptual/RemoteNotificationsPG/Chapters/TheNotificationPay
        load.html>`_ for details.

        This property is cached once computed, so it is best to not reuse
        message objects.
        """
        payload = {
            'aps': self.aps,
        }

        if self.extra:
            payload.update(self.extra)

        return payload

    @cached_property
    def encoded(self):
        """The message payload encoded as a JSON string.

        This property is cached once computed.
        """
        jsondata = json.dumps(
            self.payload,
            # Apple does not support \U notation
            ensure_ascii=False,
            # More compact than the default separators
            separators=(',', ':')
        )
        if not isinstance(jsondata, binary_type):  # pragma: no cover
            jsondata = jsondata.encode('utf-8')
        return jsondata


class Alert(object):
    """Object representing the APNs ``alert`` data of the ``aps`` payload.

    Use this to construct an alert if you need to support the Apple Watch, have
    localized notification messages, or change the launch image used when
    opening your app from a notification.

    If your notifications do not need to support these things, and you just
    want a simple text notification, you may use a regular string for
    :attr:`.Message.alert`.

    See the `APNs Remote Notification Payload`_ documentation for more details.

    :param title: A short string describing the purpose of the notification.
        Apple Watch displays this string as part of the notification interface.
        This string is displayed only briefly and should be crafted so that it
        can be understood quickly.
    :param body: The text of the alert message.
    :param title_loc_key: The key to a title string in the
        ``Localizable.strings`` file for the current localization. The key
        string can be formatted with ``%@`` and ``%n$@`` specifiers to take the
        variables specified in the title-loc-args array.
    :param title_loc_args: Variable string values to appear in place of the
        format specifiers in title-loc-key.
    :param action_loc_key: If a string is specified, the system displays an
        alert that includes the Close and View buttons. The string is used as a
        key to get a localized string in the current localization to use for
        the right button’s title instead of “View”.
    :param loc_key: A key to an alert-message string in a
        ``Localizable.strings`` file for the current localization (which is set
        by the user’s language preference). The key string can be formatted
        with ``%@`` and ``%n$@`` specifiers to take the variables specified in
        the ``loc-args`` array.
    :param loc_args: Variable string values to appear in place of the format
        specifiers in loc-key.
    :param launch_image: The filename of an image file in the app bundle; it
        may include the extension or omit it. The image is used as the launch
        image when users tap the action button or move the action slider. If
        this property is not specified, the system either uses the previous
        snapshot,uses the image identified by the ``UILaunchImageFile`` key in
        the app’s ``Info.plist`` file, or falls back to ``Default.png``.

    .. _APNs Remote Notification Payload: https://developer.apple.com/library/i
        os/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Ch
        apters/TheNotificationPayload.html
    """
    def __init__(self, title, body, title_loc_key=None, title_loc_args=None,
                 action_loc_key=None, loc_key=None, loc_args=None,
                 launch_image=None):
        self.body = body
        self.title = title
        self.title_loc_key = title_loc_key
        self.title_loc_args = title_loc_args
        self.action_loc_key = action_loc_key
        self.loc_key = loc_key
        self.loc_args = loc_args
        self.launch_image = launch_image

    @cached_property
    def payload(self):
        """The payload data that will be used for the ``alert`` section of the
        ``aps`` payload.
        """
        p = {
            'title': self.title,
            'body': self.body,
            'title-loc-key': self.title_loc_key,
            'title-loc-args': self.title_loc_args,
            'action-loc-key': self.action_loc_key,
            'loc-key': self.loc_key,
            'loc-args': self.loc_args,
            'launch-image': self.launch_image,
        }
        return {k: v for k, v in iteritems(p) if v is not None}
