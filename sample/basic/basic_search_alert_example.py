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
        exit(1)
