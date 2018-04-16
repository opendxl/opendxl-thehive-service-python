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
