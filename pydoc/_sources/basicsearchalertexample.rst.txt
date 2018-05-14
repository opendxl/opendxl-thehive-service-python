Basic Search Alert Example
==========================

This sample searches for an alert on TheHive server via TheHive ``Alert`` API.
The sample displays the results of the calls to the ``Search`` API.

For more information on TheHive ``Alert`` API, see the
`TheHive REST Alert API <https://github.com/TheHive-Project/TheHiveDocs/blob/master/api/alert.md>`__
documentation.

Prerequisites
*************

* The samples configuration step has been completed (see :doc:`sampleconfig`).
* TheHive DXL service is running, using the ``sample`` configuration
  (see :doc:`running`).
* Run through the steps in the :doc:`basiccreatealertexample`
  to store an alert to TheHive server. This example will find the last
  alert stored by running the :doc:`basiccreatealertexample`.

Running
*******

To run this sample execute the ``sample/basic/basic_search_alert_example.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_create_alert_example.py

The output should appear similar to the following:

    .. code-block:: shell

        Response for the search alert request: '[
            {
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
            }
        ]'

Details
*******

In order to enable the use of the ``search_alert`` API, the
API name is listed in the ``apiNames`` setting under the ``[General]``
section in the ``sample`` "dxlthehiveservice.config" file that the service uses:

    .. code-block:: ini

        [General]
        apiNames=...,search_alert,...

For more information on the configuration, see the
:ref:`Service Configuration File <dxl_service_config_file_label>` section.

The majority of the sample code is shown below:

    .. code-block:: python

        # Create the client
        with DxlClient(config) as client:

            # Connect to the fabric
            client.connect()

            logger.info("Connected to DXL fabric.")

            # Create the search alert request
            request_topic = "/opendxl-thehive/service/thehive-api/alert/search"
            req = Request(request_topic)

            # Set the payload for the search alert request. The request includes three
            # criteria:
            # - query: Matches only alerts with a value for the 'title' field which
            #     includes the words 'OpenDXL' and 'Alert'. This should match alerts
            #     created by running the 'basic_create_alert_example.py' example.
            # - range: A value of "0-1" causes only one entry from the result set to
            #     be returned.
            # - sort: The value "-createdAt" causes a descending sort by the value in
            #     the createdAt field in the alert to be performed on the server.
            # The response for this query should include only the most recent alert
            # created by running the 'basic_create_alert_example.py' example.
            MessageUtils.dict_to_json_payload(
                req,
                {
                    "query": {"_string": "title:(OpenDXL AND Alert)"},
                    "range": "0-1",
                    "sort": ["-createdAt"]
                })

            # Set the payload for the search alert request
            alert_search_response = client.sync_request(req, timeout=30)

            if alert_search_response.message_type is not Message.MESSAGE_TYPE_ERROR:
                # Display results for the search alert request
                alert_search_response_dict = MessageUtils.json_payload_to_dict(
                    alert_search_response)
                print("Response for the search alert request: '{0}'".format(
                    MessageUtils.dict_to_json(alert_search_response_dict,
                                              pretty_print=True)))
            else:
                print("Error invoking service with topic '{0}': {1} ({2})".format(
                    request_topic, alert_search_response.error_message,
                    alert_search_response.error_code))


After connecting to the DXL fabric, a request message is created with a topic
that targets the "search_alert" method of TheHive API DXL service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include criteria to use in searching for alerts from TheHive
server. The alert returned should have the words "OpenDXL" and "Alert" in
its "title", which is true for the alert stored by running the
:doc:`basiccreatealertexample`.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.
