.. _api:

Interface
=========

.. module:: apns

This section of the documentation covers the interface portions of ``apns``.

APNs Client Interface
---------------------

.. autodata:: apns.client.APNS_SANDBOX_HOST
.. autodata:: apns.client.APNS_PRODUCTION_HOST
.. autodata:: apns.client.DEFAULT_PORT
.. autodata:: apns.client.ALTERNATE_PORT

.. autoclass:: apns.client.Client
   :members:
   :inherited-members:

Messages
--------

.. autodata:: apns.message.HIGH_PRIORITY
.. autodata:: apns.message.LOW_PRIORITY
.. autodata:: apns.message.EXPIRE_IMMEDIATELY

.. autoclass:: apns.message.Message
   :members:
   :inherited-members:

.. autoclass:: apns.message.Alert
   :members:
   :inherited-members:


SSL Context Factories
---------------------

.. autofunction:: apns.make_ssl_context

.. autofunction:: apns.make_ossl_context
