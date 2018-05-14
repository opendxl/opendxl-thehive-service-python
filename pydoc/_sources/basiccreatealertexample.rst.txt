Basic Create Alert Example
==========================

This sample creates a new alert on TheHive server via TheHive ``Alerts`` API.
The sample then retrieves the contents of the stored alert. The sample displays
the results of the calls to the ``Create`` and ``Get`` APIs.

For more information on TheHive ``Alert`` API, see the
`TheHive REST Alert API <https://github.com/TheHive-Project/TheHiveDocs/blob/master/api/alert.md>`__
documentation.

Prerequisites
*************

* The samples configuration step has been completed (see :doc:`sampleconfig`).
* TheHive DXL service is running, using the ``sample`` configuration
  (see :doc:`running`).
* In TheHive web user interface, grant the API user permission to create alerts
  (Allow alerts creation). For more information on user administration, see
  `TheHive User Management <https://github.com/TheHive-Project/TheHiveDocs/blob/master/admin/admin-guide.md#1-user-management>`__.
  documentation.

Running
*******

To run this sample execute the ``sample/basic/basic_create_alert_example.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_create_alert_example.py

The output should appear similar to the following:

    .. code-block:: shell

        Response for the create alert request: '{
            "_id": "237c6fbc97b86f81b30365acfc7e04c8",
            "_parent": null,
            "_routing": "237c6fbc97b86f81b30365acfc7e04c8",
            "_type": "alert",
            "_version": 1,
            "artifacts": [],
            "createdAt": 1524002836273,
            "createdBy": "admin",
            "date": 1524002836301,
            "description": "Created by the OpenDXL Alert Example",
            "follow": true,
            "id": "237c6fbc97b86f81b30365acfc7e04c8",
            "lastSyncDate": 1524002836302,
            "severity": 3,
            "source": "OpenDXL",
            "sourceRef": "1471d7d94f6042cd",
            "status": "New",
            "title": "OpenDXL Alert Example",
            "tlp": 2,
            "type": "external"
        }'
        Response for the get alert request: '{
            "_id": "237c6fbc97b86f81b30365acfc7e04c8",
            "_parent": null,
            "_routing": "237c6fbc97b86f81b30365acfc7e04c8",
            "_type": "alert",
            "_version": 1,
            "artifacts": [],
            "createdAt": 1524002836273,
            "createdBy": "admin",
            "date": 1524002836301,
            "description": "Created by the OpenDXL Alert Example",
            "follow": true,
            "id": "237c6fbc97b86f81b30365acfc7e04c8",
            "lastSyncDate": 1524002836302,
            "severity": 3,
            "source": "OpenDXL",
            "sourceRef": "1471d7d94f6042cd",
            "status": "New",
            "title": "OpenDXL Alert Example",
            "tlp": 2,
            "type": "external"
        }'

Details
*******

In order to enable the use of the ``create_alert`` and ``get_alert`` APIs, both
API names are listed in the ``apiNames`` setting under the ``[General]``
section in the ``sample`` "dxlthehiveservice.config" file that the service uses:

    .. code-block:: ini

        [General]
        apiNames=...,create_alert,get_alert...

For more information on the configuration, see the
:ref:`Service Configuration File <dxl_service_config_file_label>` section.

The majority of the sample code is shown below:

    .. code-block:: python

        # Create the client
        with DxlClient(config) as client:

            # Connect to the fabric
            client.connect()

            logger.info("Connected to DXL fabric.")

            # Create the new alert request
            request_topic = "/opendxl-thehive/service/thehive-api/alert/create"
            req = Request(request_topic)

            # Generate a unique id for the alert sourceRef. A unique combination of
            # type, source, and sourceRef needs to be supplied for each new alert
            # to be created.
            unique_id = uuid.uuid4().hex[0:16]

            # Set the payload for the new alert request
            MessageUtils.dict_to_json_payload(
                req,
                {
                    "title": "OpenDXL Alert Example",
                    "description": "Created by the OpenDXL Alert Example",
                    "severity": 3,
                    "source": "OpenDXL",
                    "sourceRef": unique_id,
                    "type": "external"
                })

            # Send the new alert request
            create_alert_response = client.sync_request(req, timeout=30)

            if create_alert_response.message_type is not Message.MESSAGE_TYPE_ERROR:
                # Display results for the new alert request
                create_alert_response_dict = MessageUtils.json_payload_to_dict(
                    create_alert_response)
                print("Response for the create alert request: '{0}'".format(
                    MessageUtils.dict_to_json(create_alert_response_dict,
                                              pretty_print=True)))
            else:
                print("Error invoking service with topic '{0}': {1} ({2})".format(
                    request_topic, create_alert_response.error_message,
                    create_alert_response.error_code))
                exit(1)


After connecting to the DXL fabric, a request message is created with a topic
that targets the "create_alert" method of TheHive API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include information to store in TheHive alert.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Create the get alert request
        request_topic = "/opendxl-thehive/service/thehive-api/alert/get"
        req = Request(request_topic)

        # Set the payload for the get alert request
        MessageUtils.dict_to_json_payload(
            req,
            {
                "id": create_alert_response_dict["id"]
            })

        # Send the get alert request
        get_alert_response = client.sync_request(req, timeout=30)

        if get_alert_response.message_type is not Message.MESSAGE_TYPE_ERROR:
            # Display results for the get alert request
            get_alert_response_dict = MessageUtils.json_payload_to_dict(
                get_alert_response)
            print("Response for the get alert request: '{0}'".format(
                MessageUtils.dict_to_json(get_alert_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{0}': {1} ({2})".format(
                request_topic, get_alert_response.error_message,
                get_alert_response.error_code))


To confirm that the alert was stored properly, a second request message is
created with a topic that targets the "get_alert" method of TheHive API DXL
service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``id`` of the alert to retrieve. Note that the
``id`` used in the get request is extracted from the response
received for the prior "create_alert" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.
