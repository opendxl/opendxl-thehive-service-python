Basic Create Case Task Example
==============================

This sample creates a new case on TheHive server via TheHive ``Case`` API. The
sample then adds a task to the stored case via TheHive ``Task`` API. The sample
retrieves the case and its associated observable and displays the results of
all of the API calls.

For more information on the API methods that this example uses, see the
`TheHive REST Case API <https://github.com/TheHive-Project/TheHiveDocs/blob/master/api/case.md>`__
and
`TheHive REST Task API <https://github.com/TheHive-Project/TheHiveDocs/blob/master/api/task.md>`__
documentation.

Prerequisites
*************

* The samples configuration step has been completed (see :doc:`sampleconfig`).
* TheHive DXL service is running, using the ``sample`` configuration
  (see :doc:`running`).

Running
*******

To run this sample execute the ``sample/basic/basic_create_task_example.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_create_task_example.py

The output should appear similar to the following:

    .. code-block:: shell

        Response for the create case request: '{
            "_id": "AWLVqVBjEL_PtpkToK_B",
            "_parent": null,
            "_routing": "AWLVqVBjEL_PtpkToK_B",
            "_type": "case",
            "_version": 1,
            "caseId": 91,
            "createdAt": 1524003064979,
            "createdBy": "admin",
            "customFields": {},
            "description": "Created by the OpenDXL Case Task Example",
            "flag": false,
            "id": "AWLVqVBjEL_PtpkToK_B",
            "metrics": {},
            "owner": "admin",
            "severity": 3,
            "startDate": 1524003065953,
            "status": "Open",
            "title": "OpenDXL Case Task Example",
            "tlp": 2
        }'
        Response for the get case request: '{
            "_id": "AWLVqVBjEL_PtpkToK_B",
            "_parent": null,
            "_routing": "AWLVqVBjEL_PtpkToK_B",
            "_type": "case",
            "_version": 1,
            "caseId": 91,
            "createdAt": 1524003064979,
            "createdBy": "admin",
            "customFields": {},
            "description": "Created by the OpenDXL Case Task Example",
            "flag": false,
            "id": "AWLVqVBjEL_PtpkToK_B",
            "metrics": {},
            "owner": "admin",
            "severity": 3,
            "startDate": 1524003065953,
            "status": "Open",
            "title": "OpenDXL Case Task Example",
            "tlp": 2
        }'
        Response for the create case task request: '{
            "_id": "AWLVqVSlEL_PtpkToK_D",
            "_parent": "AWLVqVBjEL_PtpkToK_B",
            "_routing": "AWLVqVBjEL_PtpkToK_B",
            "_type": "case_task",
            "_version": 1,
            "createdAt": 1524003067041,
            "createdBy": "admin",
            "description": "Created by the OpenDXL Case Task Example",
            "flag": false,
            "id": "AWLVqVSlEL_PtpkToK_D",
            "order": 0,
            "status": "InProgress",
            "title": "OpenDXL Case Task Example"
        }'
        Response for the get case task request: '{
            "_id": "AWLVqVSlEL_PtpkToK_D",
            "_parent": "AWLVqVBjEL_PtpkToK_B",
            "_routing": "AWLVqVBjEL_PtpkToK_B",
            "_type": "case_task",
            "_version": 1,
            "createdAt": 1524003067041,
            "createdBy": "admin",
            "description": "Created by the OpenDXL Case Task Example",
            "flag": false,
            "id": "AWLVqVSlEL_PtpkToK_D",
            "order": 0,
            "status": "InProgress",
            "title": "OpenDXL Case Task Example"
        }'

Details
*******

In order to enable the various APIs used by this sample, each of the API names
are listed in the ``apiNames`` setting under the ``[General]`` section in the
``sample`` "dxlthehiveservice.config" file that the service uses:

    .. code-block:: ini

        [General]
        apiNames=create_case,...,create_case_task,...,get_case,...,get_case_task,...

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
                    "title": "OpenDXL Case Task Example",
                    "description": "Created by the OpenDXL Case Task Example",
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

        # Create the new case task request
        request_topic = "/opendxl-thehive/service/thehive-api/case/task/create"
        req = Request(request_topic)

        # Set the payload for the new case task request
        MessageUtils.dict_to_json_payload(
            req,
            {
                "caseId": case_id,
                "title": "OpenDXL Case Task Example",
                "description":
                    "Created by the OpenDXL Case Task Example",
                "status": "InProgress"
            })

        # Send the new case task request
        create_case_task_response = client.sync_request(req, timeout=30)

        if create_case_task_response.message_type is not Message.MESSAGE_TYPE_ERROR:
            # Display results for the new case task request
            create_case_task_response_dict = MessageUtils.json_payload_to_dict(
                create_case_task_response)
            print("Response for the create case task request: '{0}'".format(
                MessageUtils.dict_to_json(create_case_task_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{0}': {1} ({2})".format(
                request_topic, create_case_task_response.error_message,
                create_case_task_response.error_code))
            exit(1)


A request message is then created with a topic that targets the
"create_case_task" method of TheHive API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``id`` of the case to associate the task with.
Note that the ``id`` used in the request is extracted from the response
received for the prior "create_case" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Create the get case task request
        request_topic = "/opendxl-thehive/service/thehive-api/case/task/get"
        req = Request(request_topic)

        # Set the payload for the get case task request
        MessageUtils.dict_to_json_payload(
            req,
            {
                "id": create_case_task_response_dict["id"]
            })

        # Send the get case task request
        get_case_task_response = client.sync_request(req, timeout=30)

        if get_case_task_response.message_type is not Message.MESSAGE_TYPE_ERROR:
            # Display results for the get case task request
            get_case_task_response_dict = MessageUtils.json_payload_to_dict(
                get_case_task_response)
            print("Response for the get case task request: '{0}'".format(
                MessageUtils.dict_to_json(get_case_task_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{0}': {1} ({2})".format(
                request_topic, get_case_task_response.error_message,
                get_case_task_response.error_code))


To confirm that the task was stored properly, a request message is
created with a topic that targets the "get_case_task" method of TheHive
API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``id`` of the task to retrieve. Note that the
``id`` used in the get request is extracted from the response received for the
prior "create_case_task" request.

The final step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.
