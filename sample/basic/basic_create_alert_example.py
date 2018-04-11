from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import uuid

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
