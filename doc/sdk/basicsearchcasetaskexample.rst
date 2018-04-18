Basic Search Case Task Example
==============================

This sample searches for a case on TheHive server via TheHive ``Case`` API. The
sample then searches for all of the tasks associated with the case via TheHive
``Task`` API. The sample displays the results of the calls to the ``Search``
APIs.

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
* Run through the steps in the :doc:`basiccreatecasetaskexample` to store a
  case and an associated observable to TheHive server. This example will find
  the tasks for the last case stored by running the
  :doc:`basiccreatecasetaskexample` .

Running
*******

To run this sample execute the ``sample/basic/basic_search_case_task_example.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_search_case_task_example.py

The output should appear similar to the following:

    .. code-block:: shell

        Response for the search case request: '[
            {
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
            }
        ]'
        Response for the search case task request: '[
            {
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
            }
        ]'

Details
*******

In order to enable the use of the ``search_case`` and ``search_case_task``
APIs, both API names are listed in the ``apiNames`` setting under the
``[General]`` section in the ``sample`` "dxlthehiveservice.config" file that
the service uses:

    .. code-block:: ini

        [General]
        apiNames=...,search_case,search_case_task,...

For more information on the configuration, see the
:ref:`Service Configuration File <dxl_service_config_file_label>` section.

The majority of the sample code is shown below:

    .. code-block:: python

        # Create the client
        with DxlClient(config) as client:

            # Connect to the fabric
            client.connect()

            logger.info("Connected to DXL fabric.")

            # Create the search case request
            request_topic = "/opendxl-thehive/service/thehive-api/case/search"
            req = Request(request_topic)

            # Set the payload for the search case request. The request includes two
            # criteria:
            # - query: Matches only cases with a value for the 'title' field which
            #     includes the words 'OpenDXL' and 'Task'. This should match
            #     cases created by running the
            #     'basic_create_case_task_example.py' example.
            # - range: A value of "0-1" causes only one entry from the result set to
            #     be returned.
            # The response for this query should include only the most recent case
            # created by running the 'basic_create_case_task_example.py' example.
            MessageUtils.dict_to_json_payload(
                req,
                {
                    "query": {"_string": "title:(OpenDXL AND Task)"},
                    "range": "0-1"
                })

            # Set the payload for the search case request
            case_search_response = client.sync_request(req, timeout=30)

            if case_search_response.message_type is not Message.MESSAGE_TYPE_ERROR:
                # Display results for the search case request
                case_search_response_dict = MessageUtils.json_payload_to_dict(
                    case_search_response)
                print("Response for the search case request: '{0}'".format(
                    MessageUtils.dict_to_json(case_search_response_dict,
                                              pretty_print=True)))
            else:
                print("Error invoking service with topic '{0}': {1} ({2})".format(
                    request_topic, case_search_response.error_message,
                    case_search_response.error_code))
                exit(1)


After connecting to the DXL fabric, a request message is created with a topic
that targets the "search_case" method of TheHive API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include criteria to use in the search for cases from TheHive
server. The case returned should have the words "OpenDXL" and "Task" in its
"title", which is true for the case stored by running the
:doc:`basiccreatecasetaskexample` .

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        if case_search_response_dict:
            # Extract the id of the case from the results of the search case request
            case_id = case_search_response_dict[0]["id"]

            # Create the search case task request
            request_topic = "/opendxl-thehive/service/thehive-api/case/task/search"
            req = Request(request_topic)

            # Set the payload for the search case task request. The query should
            # return all tasks associated with the case id from the prior search
            # case request.
            MessageUtils.dict_to_json_payload(
                req,
                {
                    "query": {"_parent": {"_type": "case",
                                          "_query": {"_id": case_id}}}
                })

            # Set the payload for the search case task request
            get_case_task_response = client.sync_request(req, timeout=30)
            if get_case_task_response.message_type is not Message.MESSAGE_TYPE_ERROR:
                # Display results for the search case task request
                get_case_response_dict = MessageUtils.json_payload_to_dict(
                    get_case_task_response)
                print("Response for the search case task request: '{0}'".format(
                    MessageUtils.dict_to_json(get_case_response_dict,
                                              pretty_print=True)))
            else:
                print("Error invoking service with topic '{0}': {1} ({2})".format(
                    request_topic, get_case_task_response.error_message,
                    get_case_task_response.error_code))
        else:
            print("No cases available to search for tasks")


If a case was found from the prior search, a second request message is created
with a topic that targets the "search_case_task" method of TheHive API DXL
service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``id`` of the case associated with the tasks to
retrieve. Note that the ``id`` used in the search request is extracted from the
response received for the prior "search_case" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.
