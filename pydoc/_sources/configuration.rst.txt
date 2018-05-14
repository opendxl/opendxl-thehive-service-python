Configuration
=============

TheHive DXL Python Service application requires a set of configuration files to operate.

This distribution contains a ``config`` sub-directory that includes the configuration files that must
be populated prior to running the application.

Each of these files are documented throughout the remainder of this page.

Application configuration directory:

    .. code-block:: python

        config/
            dxlclient.config
            dxlthehiveservice.config
            logging.config (optional)

.. _dxl_client_config_file_label:

DXL Client Configuration File (dxlclient.config)
------------------------------------------------

    The required ``dxlclient.config`` file is used to configure the DXL client that will connect to the DXL fabric.

    The steps to populate this configuration file are the same as those documented in the `OpenDXL Python
    SDK`, see the
    `OpenDXL Python SDK Samples Configuration <https://opendxl.github.io/opendxl-client-python/pydoc/sampleconfig.html>`_
    page for more information.

    The following is an example of a populated DXL client configuration file:

        .. code-block:: python

            [Certs]
            BrokerCertChain=c:\\certificates\\brokercerts.crt
            CertFile=c:\\certificates\\client.crt
            PrivateKey=c:\\certificates\\client.key

            [Brokers]
            {5d73b77f-8c4b-4ae0-b437-febd12facfd4}={5d73b77f-8c4b-4ae0-b437-febd12facfd4};8883;mybroker.mcafee.com;192.168.1.12
            {24397e4d-645f-4f2f-974f-f98c55bdddf7}={24397e4d-645f-4f2f-974f-f98c55bdddf7};8883;mybroker2.mcafee.com;192.168.1.13

.. _dxl_service_config_file_label:

TheHive DXL Python Service (dxlthehiveservice.config)
-----------------------------------------------------

    The required ``dxlthehiveservice.config`` file is used to configure the application.

    The following is an example of a populated application configuration file:

        .. code-block:: ini

            [General]
            host=thehiveserver1
            apiPrincipal=12345
            apiNames=create_case,search_case_task,create_alert
            verifyCertificate=yes
            verifyCertBundle=thehiveCA.crt

    **General**

        The ``[General]`` section is used to specify TheHive server
        configuration and TheHive API methods which should be available to
        invoke via DXL.

        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | Name                             | Required | Description                                                                                            |
        +==================================+==========+========================================================================================================+
        | host                             | yes      | TheHive server hostname or IP address.                                                                 |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | apiNames                         | yes      | The list of TheHive APIs for which corresponding request topics should be exposed                      |
        |                                  |          | to the DXL fabric, delimited by commas.                                                                |
        |                                  |          |                                                                                                        |
        |                                  |          | For example:                                                                                           |
        |                                  |          |                                                                                                        |
        |                                  |          | ``create_case,search_case_task,create_alert``                                                          |
        |                                  |          |                                                                                                        |
        |                                  |          | With this example and the ``serviceUniqueId`` setting set to                                           |
        |                                  |          | ``sample``, the request topics exposed to the DXL fabric would be:                                     |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-thehive/service/thehive-api/sample/create_case``                                            |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-thehive/service/thehive-api/sample/search_case_task``                                       |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-thehive/service/thehive-api/sample/create_alert``                                           |
        |                                  |          |                                                                                                        |
        |                                  |          | The complete list of available API method names and parameters is available                            |
        |                                  |          | in the documentation at                                                                                |
        |                                  |          | https://github.com/opendxl/opendxl-thehive-service-python/wiki/Service-Methods.                        |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | serviceUniqueId                  | no       | An optional unique identifier used to identify the                                                     |
        |                                  |          | opendxl-thehive service on the DXL fabric. If set, this                                                |
        |                                  |          | unique identifier will be appended to the name of each request topic                                   |
        |                                  |          | used on the fabric. For example, if the serviceUniqueId is                                             |
        |                                  |          | set to ``sample``, the request topic names would start with the                                        |
        |                                  |          | following:                                                                                             |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-thehive/service/thehive-api/sample/<method>``                                               |
        |                                  |          |                                                                                                        |
        |                                  |          | If serviceUniqueId is not set, request topic names would not                                           |
        |                                  |          | include an id segment, for example:                                                                    |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-thehive/service/thehive-api/<method>``                                                      |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | apiPrincipal                     | yes      | TheHive server's API principal. If ``apiPassword`` is specified, the principal                         |
        |                                  |          | is treated as a user name. If ``apiPassword`` is empty or not specified, the                           |
        |                                  |          | principal is treated as an API key.                                                                    |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | apiPassword                      | no       | TheHive server's API password.                                                                         |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | port                             | no       | TheHive server's HTTP API port. Defaults to ``9443`` if useSSL is ``yes``.                             |
        |                                  |          | If useSSL is no, defaults to ``9000``.                                                                 |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | useSSL                           | no       | Whether or not to use SSL/TLS for requests made to TheHive server. If set to                           |
        |                                  |          | ``yes``, SSL/TLS is used. Defaults to ``yes``.                                                         |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | verifyCertificate                | no       | Whether to verify that TheHive server's certificate was                                                |
        |                                  |          | signed by a valid certificate authority when SSL/TLS is being                                          |
        |                                  |          | used. Defaults to ``yes``.                                                                             |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | verifyCertBundle                 | no       | A path to a CA Bundle file containing certificates of trusted                                          |
        |                                  |          | CAs. The CA Bundle is used to ensure that TheHive                                                      |
        |                                  |          | server being connected to was signed by a valid authority. Only                                        |
        |                                  |          | applicable if ``verifyCertificate`` is ``yes``.                                                        |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+


Logging File (logging.config)
-----------------------------

    The optional ``logging.config`` file is used to configure how the application writes log messages.
