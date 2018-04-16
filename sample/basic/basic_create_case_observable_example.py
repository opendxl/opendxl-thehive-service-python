from __future__ import absolute_import
from __future__ import print_function
import os
import sys

from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlclient.message import Message, Request
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
