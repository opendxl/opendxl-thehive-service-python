from __future__ import absolute_import
import logging

from dxlclient.callbacks import RequestCallback
from dxlclient.message import ErrorResponse
from dxlbootstrap.util import MessageUtils

# Configure local logger
logger = logging.getLogger(__name__)


class TheHiveApiRequestCallback(RequestCallback):
    def __init__(self, dxl_client, thehive_client):
        """
        Constructor parameters:

        :param dxlclient.client.DxlClient dxl_client: DXL client through which
            responses can be sent.
        :param dxlthehiveservice.thehive_client.TheHiveClient thehive_client:
            HTTP client through which requests to TheHive server should be sent.
        """
        super(TheHiveApiRequestCallback, self).__init__()
        self._dxl_client = dxl_client
        self._thehive_client = thehive_client

    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        logger.info("Request received on topic: '%s' with payload: '%s'",
                    request.destination_topic,
                    MessageUtils.decode_payload(request))

    def _pop_attribute_from_request(self, request, attr_name):
        """
        Pop the value for a named attribute from the supplied request JSON
        and return the remaining request body.
        :param request:
        :param attr_name:
        :return:
        :raises ValueError: if the named attribute does not appear in the
            request.
        :return: A tuple containing two elements: the value associated with
            the attr_name parameter and the request body (minus the attr_name
            attribute and its associated value), converted to a dict.
        :rtype: tuple
        """
        try:
            request_body = MessageUtils.json_payload_to_dict(request)
            attr_value = request_body.pop(attr_name, None)
            if not attr_name:
                raise ValueError("Attribute {} is missing".format(attr_name))
        except Exception as ex:
            request_body = {}
            attr_value = None
            error_str = str(ex)
            logger.exception("Error handling request: %s", error_str)
            res = ErrorResponse(request,
                                error_message=MessageUtils.encode(error_str))
            self._dxl_client.send_response(res)
        return (attr_value, request_body)


class TheHiveCreateCaseRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/create
    DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveCreateCaseRequestCallback, self).on_request(request)
        self._thehive_client.post(request, "/api/case")


class TheHiveCreateCaseTaskRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/task/create
    DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveCreateCaseTaskRequestCallback, self).on_request(request)
        case_id, request_body = self._pop_attribute_from_request(request,
                                                                 "caseId")
        if case_id:
            self._thehive_client.post(
                request, "/api/case/{}/task".format(case_id), request_body)


class TheHiveCreateCaseObservableRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/observable/create
    DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveCreateCaseObservableRequestCallback, self).on_request(
            request)
        case_id, request_body = self._pop_attribute_from_request(request,
                                                                 "caseId")
        if case_id:
            self._thehive_client.post(
                request, "/api/case/{}/artifact".format(case_id), request_body)


class TheHiveGetCaseRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/get DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveGetCaseRequestCallback, self).on_request(request)
        case_id = self._pop_attribute_from_request(request, "id")[0]
        if case_id:
            self._thehive_client.get(request, "/api/case/{}".format(case_id))


class TheHiveGetCaseTaskRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/task/get DXL
    requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveGetCaseTaskRequestCallback, self).on_request(request)
        task_id = self._pop_attribute_from_request(request, "id")[0]
        if task_id:
            self._thehive_client.get(request,
                                     "/api/case/task/{}".format(task_id))


class TheHiveGetCaseObservableRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/observable/get
    DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveGetCaseObservableRequestCallback, self).on_request(request)
        observable_id = self._pop_attribute_from_request(request, "id")[0]
        if observable_id:
            self._thehive_client.get(request,
                                     "/api/case/artifact/{}".format(
                                         observable_id))

class TheHiveSearchCaseRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/search DXL
    requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveSearchCaseRequestCallback, self).on_request(request)
        self._thehive_client.post(request, "/api/case/_search")


class TheHiveSearchCaseTaskRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/task/search
    DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveSearchCaseTaskRequestCallback, self).on_request(request)
        self._thehive_client.post(request, "/api/case/task/_search")


class TheHiveSearchCaseObservableRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for case/observable/search
    DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveSearchCaseObservableRequestCallback, self).on_request(request)
        self._thehive_client.post(request, "/api/case/artifact/_search")


class TheHiveCreateAlertRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for alert/create DXL
    requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveCreateAlertRequestCallback, self).on_request(request)
        self._thehive_client.post(request, "/api/alert")


class TheHiveGetAlertRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for alert/get DXL requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveGetAlertRequestCallback, self).on_request(request)
        case_id = self._pop_attribute_from_request(request, "id")[0]
        if case_id:
            self._thehive_client.get(request, "/api/alert/{}".format(case_id))


class TheHiveSearchAlertRequestCallback(TheHiveApiRequestCallback):
    """
    Request callback used to invoke TheHive REST API for alert/search DXL
    requests.
    """
    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param dxlclient.message.Request request: The request message
        """
        super(TheHiveSearchAlertRequestCallback, self).on_request(request)
        self._thehive_client.post(request, "/api/alert/_search")
