Basic Create Case Observable Example
====================================

This sample creates a new case on TheHive server via TheHive ``Case`` API. The
sample then adds an observable to the stored case via TheHive ``Observable``
API. The sample retrieves the case and its associated observable and displays
the results of all of the API calls.

For more information on the API methods that this example uses, see the
`TheHive REST Case API <https://github.com/TheHive-Project/TheHiveDocs/blob/master/api/case.md>`__
and
`TheHive REST Observable API <https://github.com/TheHive-Project/TheHiveDocs/blob/master/api/artifact.md>`__
documentation.

Prerequisites
*************

* The samples configuration step has been completed (see :doc:`sampleconfig`).
* TheHive DXL service is running, using the ``sample`` configuration
  (see :doc:`running`).

Running
*******

To run this sample execute the ``sample/basic/basic_create_case_observable_example.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_create_case_observable_example.py

The output should appear similar to the following:

    .. code-block:: shell

        Response for the create case request: '{
            "_id": "AWLVqGV4EL_PtpkToK8t",
            "_parent": null,
            "_routing": "AWLVqGV4EL_PtpkToK8t",
            "_type": "case",
            "_version": 1,
            "caseId": 90,
            "createdAt": 1524003005674,
            "createdBy": "admin",
            "customFields": {},
            "description": "Created by the OpenDXL Case Observable Example",
            "flag": false,
            "id": "AWLVqGV4EL_PtpkToK8t",
            "metrics": {},
            "owner": "admin",
            "severity": 3,
            "startDate": 1524003005814,
            "status": "Open",
            "title": "OpenDXL Case Observable Example",
            "tlp": 2
        }'
        Response for the get case request: '{
            "_id": "AWLVqGV4EL_PtpkToK8t",
            "_parent": null,
            "_routing": "AWLVqGV4EL_PtpkToK8t",
            "_type": "case",
            "_version": 1,
            "caseId": 90,
            "createdAt": 1524003005674,
            "createdBy": "admin",
            "customFields": {},
            "description": "Created by the OpenDXL Case Observable Example",
            "flag": false,
            "id": "AWLVqGV4EL_PtpkToK8t",
            "metrics": {},
            "owner": "admin",
            "severity": 3,
            "startDate": 1524003005814,
            "status": "Open",
            "title": "OpenDXL Case Observable Example",
            "tlp": 2
        }'
        Response for the create case observable request: '{
            "_id": "7179b9c6564146841b69bfe0699013db",
            "_parent": "AWLVqGV4EL_PtpkToK8t",
            "_routing": "AWLVqGV4EL_PtpkToK8t",
            "_type": "case_artifact",
            "_version": 1,
            "createdAt": 1524003006922,
            "createdBy": "admin",
            "data": "OpenDXL",
            "dataType": "user-agent",
            "id": "7179b9c6564146841b69bfe0699013db",
            "ioc": false,
            "message": "Created by the OpenDXL Case Observable Example",
            "reports": {},
            "sighted": false,
            "startDate": 1524003006946,
            "status": "Ok",
            "tags": [],
            "tlp": 2
        }'
        Response for the get case observable request: '{
            "_id": "7179b9c6564146841b69bfe0699013db",
            "_parent": "AWLVqGV4EL_PtpkToK8t",
            "_routing": "AWLVqGV4EL_PtpkToK8t",
            "_type": "case_artifact",
            "_version": 1,
            "createdAt": 1524003006922,
            "createdBy": "admin",
            "data": "OpenDXL",
            "dataType": "user-agent",
            "id": "7179b9c6564146841b69bfe0699013db",
            "ioc": false,
            "message": "Created by the OpenDXL Case Observable Example",
            "reports": {},
            "sighted": false,
            "startDate": 1524003006946,
            "status": "Ok",
            "tags": [],
            "tlp": 2
        }'

Details
*******

In order to enable the various APIs used by this sample, each of the API names
are listed in the ``apiNames`` setting under the ``[General]`` section in the
``sample`` "dxlthehiveservice.config" file that the service uses:

    .. code-block:: ini

        [General]
        apiNames=create_case,...,create_case_observable,...,get_case,...,get_case_observable,...

For more information on the configuration, see the
:ref:`Service Configuration File <dxl_service_config_file_label>` section.

The majority of the sample code is shown below:

    .. code-block:: python

        # Create the client
        with DxlClient(config) as client:

            # Connect to the fabric
            client.connect()

            logger.info("Connected to DXL fabric.")

            # Create the new case request
            request_topic = "/opendxl-thehive/service/thehive-api/case/create"
            req = Request(request_topic)

            # Set the payload for the new case request
            MessageUtils.dict_to_json_payload(
                req,
                {
                    "title": "OpenDXL Case Observable Example",
                    "description": "Created by the OpenDXL Case Observable Example",
                    "severity": 3
                })

            # Send the new case request
            create_case_response = client.sync_request(req, timeout=30)

            if create_case_response.message_type is not Message.MESSAGE_TYPE_ERROR:
                # Display results for the new case request
                create_case_response_dict = MessageUtils.json_payload_to_dict(
                    create_case_response)
                print("Response for the create case request: '{0}'".format(
                    MessageUtils.dict_to_json(create_case_response_dict,
                                              pretty_print=True)))
            else:
                print("Error invoking service with topic '{0}': {1} ({2})".format(
                    request_topic, create_case_response.error_message,
                    create_case_response.error_code))
                exit(1)


After connecting to the DXL fabric, a request message is created with a topic
that targets the "create_case" method of TheHive API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include information to store in TheHive case.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Extract the id of the new case from the results of the new case request
        case_id = create_case_response_dict["id"]

        # Create the get case request
        request_topic = "/opendxl-thehive/service/thehive-api/case/get"
        req = Request(request_topic)

        # Set the payload for the get case request
        MessageUtils.dict_to_json_payload(
            req,
            {
                "id": case_id
            })

        # Send the get case request
        get_case_response = client.sync_request(req, timeout=30)

        if get_case_response.message_type is not Message.MESSAGE_TYPE_ERROR:
            # Display results for the get case request
            get_case_response_dict = MessageUtils.json_payload_to_dict(
                get_case_response)
            print("Response for the get case request: '{0}'".format(
                MessageUtils.dict_to_json(get_case_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{0}': {1} ({2})".format(
                request_topic, get_case_response.error_message,
                get_case_response.error_code))


To confirm that the case was stored properly, a request message is created with
a topic that targets the "get_case" method of TheHive API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``id`` of the case to retrieve. Note that the
``id`` used in the get request is extracted from the response
received for the prior "create_case" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Create the new case observable request
        request_topic = "/opendxl-thehive/service/thehive-api/case/observable/create"
        req = Request(request_topic)

        # Set the payload for the new case observable request
        MessageUtils.dict_to_json_payload(
            req,
            {
                "caseId": case_id,
                "data": "OpenDXL",
                "message": "Created by the OpenDXL Case Observable Example",
                "dataType": "user-agent"
            })

        # Send the new case observable request
        create_case_observable_response = client.sync_request(req, timeout=30)

        if create_case_observable_response.message_type is not Message.MESSAGE_TYPE_ERROR:
            # Display results for the new case observable request
            create_case_observable_response_dict = MessageUtils.json_payload_to_dict(
                create_case_observable_response)
            print("Response for the create case observable request: '{0}'".format(
                MessageUtils.dict_to_json(create_case_observable_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{0}': {1} ({2})".format(
                request_topic, create_case_observable_response.error_message,
                create_case_observable_response.error_code))
            exit(1)


A request message is then created with a topic that targets the
"create_case_observable" method of TheHive API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``id`` of the case to associate the observable with.
Note that the ``id`` used in the request is extracted from the response
received for the prior "create_case" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Create the get case observable request
        request_topic = "/opendxl-thehive/service/thehive-api/case/observable/get"
        req = Request(request_topic)

        # Set the payload for the get case observable request
        MessageUtils.dict_to_json_payload(
            req,
            {
                "id": create_case_observable_response_dict["id"]
            })

        # Send the get case observable request
        get_case_observable_response = client.sync_request(req, timeout=30)

        if get_case_observable_response.message_type is not Message.MESSAGE_TYPE_ERROR:
            # Display results for the get case observable request
            get_case_observable_response_dict = MessageUtils.json_payload_to_dict(
                get_case_observable_response)
            print("Response for the get case observable request: '{0}'".format(
                MessageUtils.dict_to_json(get_case_observable_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{0}': {1} ({2})".format(
                request_topic, get_case_observable_response.error_message,
                get_case_observable_response.error_code))


To confirm that the observable was stored properly, a request message is
created with a topic that targets the "get_case_observable" method of TheHive
API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``id`` of the observable to retrieve. Note that the
``id`` used in the get request is extracted from the response received for the
prior "create_case_observable" request.

The final step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.
