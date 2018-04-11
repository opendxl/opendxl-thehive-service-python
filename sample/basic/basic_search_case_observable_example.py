from __future__ import absolute_import
from __future__ import print_function
import os
import sys

from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlclient.message import Message, Event, Request
from dxlbootstrap.util import MessageUtils

# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

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
    # - query: Matches only alerts with a value for the 'title' field which
    #     includes the words 'OpenDXL' and 'Observable'. This should match
    #     alerts created by running the
    #     'basic_create_case_observable_example.py' example.
    # - range: A value of "0-1" causes only one entry from the result set to
    #     be returned.
    # The response for this query should include only the most recent case
    # created by running the 'basic_create_case_observable_example.py' example.
    MessageUtils.dict_to_json_payload(
        req,
        {
            "query": {"_string": "title:(OpenDXL AND Observable)"},
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

    if len(case_search_response_dict):
        # Extract the id of the case from the results of the search case request
        case_id = case_search_response_dict[0]["id"]

        # Create the search case observable request
        request_topic = "/opendxl-thehive/service/thehive-api/case/observable/search"
        req = Request(request_topic)

        # Set the payload for the search case observable request. The query
        # should return all observables associated with the case id from the
        # prior search case request.
        MessageUtils.dict_to_json_payload(
            req,
            {
                "query": {"_parent": {"_type": "case",
                                      "_query": {"_id": case_id}}}
            })

        # Set the payload for the search case observable request
        get_case_observable_response = client.sync_request(req, timeout=30)
        if get_case_observable_response.message_type is not Message.MESSAGE_TYPE_ERROR:
            # Display results for the search case observable request
            get_case_response_dict = MessageUtils.json_payload_to_dict(
                get_case_observable_response)
            print("Response for the search case observable request: '{0}'".format(
                MessageUtils.dict_to_json(get_case_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{0}': {1} ({2})".format(
                request_topic, get_case_observable_response.error_message,
                get_case_observable_response.error_code))
    else:
        print("No cases available to search for observables")
