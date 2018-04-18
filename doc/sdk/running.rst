Running
=======

Once the application library has been installed and the configuration files are populated it can be started by
executing the following command line:

    .. parsed-literal::

        python -m dxlthehiveservice <configuration-directory>

    The ``<configuration-directory>`` argument must point to a directory containing the configuration files
    required for the application (see :doc:`configuration`).

For example:

    .. parsed-literal::

        python -m dxlthehiveservice config

Output
------

The output from starting the service with the ``sample`` sub-directory
configuration should appear similar to the following:

    .. code-block:: shell

        Running application ...
        On 'run' callback.
        On 'load configuration' callback.
        Incoming message configuration: queueSize=1000, threadCount=10
        Message callback configuration: queueSize=1000, threadCount=10
        Attempting to connect to DXL fabric ...
        Waiting for broker list...
        Trying to connect...
        Trying to connect to broker {Unique id: dockerhost, Host name: 192.168.99.100, IP address: 192.168.99.100, Port: 8883}...
        Connected to broker dockerhost
        Connected to DXL fabric.
        Registering service: thehive_service
        Connecting to API URL: http://192.168.99.100:9000
        Registering request callback: thehive_create_case_requesthandler
        Registering request callback: thehive_create_case_task_requesthandler
        Registering request callback: thehive_create_case_observable_requesthandler
        Registering request callback: thehive_get_case_requesthandler
        Registering request callback: thehive_get_case_task_requesthandler
        Registering request callback: thehive_get_case_observable_requesthandler
        Registering request callback: thehive_search_case_requesthandler
        Registering request callback: thehive_search_case_task_requesthandler
        Registering request callback: thehive_search_case_observable_requesthandler
        Registering request callback: thehive_create_alert_requesthandler
        Registering request callback: thehive_get_alert_requesthandler
        Registering request callback: thehive_search_alert_requesthandler
        On 'DXL connect' callback.
