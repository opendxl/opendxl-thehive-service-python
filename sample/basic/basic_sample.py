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

    # Send request that will trigger request callback 'thehive_service_createcase'
    request_topic = "/opendxl-thehive/service/case/create"
    req = Request(request_topic)
    MessageUtils.encode_payload(req, "thehive_service_createcase request payload")
    res = client.sync_request(req, timeout=30)
    if res.message_type is not Message.MESSAGE_TYPE_ERROR:
        print("Response for thehive_service_createcase: '{0}'".format(
            MessageUtils.decode_payload(res)))
    else:
        print("Error invoking service with topic '{0}': {1} ({2})".format(
            request_topic, res.error_message, res.error_code))
