from __future__ import absolute_import
import logging

import requests
from requests.auth import HTTPBasicAuth

from dxlclient.message import Response, ErrorResponse
from dxlbootstrap.util import MessageUtils

# Configure local logger
logger = logging.getLogger(__name__)


class TheHiveClient:
    """
    HTTP client through which requests to TheHive server should be sent.
    """
    def __init__(self, dxl_client, api_url, api_key,
                 api_user, api_password, verify_certificate):
        """
        Constructor parameters:
        :param dxlclient.client.DxlClient dxl_client: DXL client through which
            responses can be sent.
        :param str api_url: URL of TheHive API server.
        :param str api_key: API key to use for requests made to TheHive server.
        :param str api_user: API user to use for requests made to TheHive server.
        :param str api_password: API password to use for requests made to
            TheHive server.
        :param verify_certificate: For a value of False, do not verify the
            server certificate in requests. For a value of True, verify the
            server certificate using the default trust store. For a string
            value, read the associated file name contents and use as a
            certificate trust store.
        """
        self._dxl_client = dxl_client
        self._api_url = api_url
        self._request_headers = \
            {"Authorization": "Bearer {}".format(api_key)} if api_key else {}
        self._request_auth = (api_user, api_password) \
            if api_user and api_password else None
        self._verify_certificate = verify_certificate

    def _request(self, dxl_request, path, request_fn, body=None):
        """
        Make a request to TheHive server, delivering the response to the
        DXL fabric.

        :param dxlclient.client.Request dxl_request: DXL request containing
            parameters to forward along in a request to TheHive server.
        :param str path: URL subpath for the request to send to TheHive server.
        :param function request_fn: Callback which is invoked to make
            TheHive request.
        :param str body: Request body to include in the request.
        """
        try:
            request_url = self._api_url + path
            response = request_fn(request_url, body)
            if 200 <= response.status_code <= 299:
                # TheHive request was successful so forward the response
                # along as-is to the DXL fabric.
                res = Response(dxl_request)
                MessageUtils.dict_to_json_payload(res, response.json())
            else:
                # TheHive request encountered an error. Attempt to decode
                # an error message from the response body.
                try:
                    response_dict = response.json()
                    error_message = response_dict.get("message")
                    if not error_message:
                        errors = response_dict.get("errors")
                        if errors:
                            first_error = errors[0]
                            if isinstance(first_error, dict):
                                error_message = first_error.get("message")
                            elif isinstance(first_error, list):
                                first_suberror = first_error[0]
                                if isinstance(first_suberror, dict):
                                    error_message = first_suberror.get(
                                        "message")
                    if error_message:
                        log_message = "Error handling request: {}".format(
                            error_message
                        )
                    else:
                        # Short error message could not be read from the
                        # response body, so just set a generic description for
                        # the error message in the DXL response.
                        error_message = "Error handling request"
                        log_message = error_message
                    logger.error(log_message)
                    res = ErrorResponse(
                        dxl_request,
                        error_message=error_message \
                            if error_message else "Error handling request",
                        error_code=response.status_code
                    )
                    MessageUtils.dict_to_json_payload(res, response_dict)
                except Exception:
                    raise
        except Exception as ex:
            error_str = str(ex)
            logger.exception("Error handling request: %s", error_str)
            res = ErrorResponse(dxl_request,
                                error_message=MessageUtils.encode(error_str))
        self._dxl_client.send_response(res)

    def get(self, dxl_request, path):
        """
        Perform an HTTP GET request to TheHive server, delivering the response
        to the DXL fabric.

        :param dxlclient.client.Request dxl_request: DXL request containing
            parameters to forward along in a request to TheHive server.
        :param str path: URL subpath for the request to send to TheHive server.
        """
        def _handle_request(request_url, _):
            return requests.get(request_url,
                                headers=self._request_headers,
                                auth=self._request_auth,
                                verify=self._verify_certificate)
        self._request(dxl_request, path, _handle_request)

    def post(self, dxl_request, path, body=None):
        """
        Perform an HTTP POST request to TheHive server, delivering the response
        to the DXL fabric.

        :param dxlclient.client.Request dxl_request: DXL request containing
            parameters to forward along in a request to TheHive server.
        :param str path: URL subpath for the request to send to TheHive server.
        :param str body: Body to include in the HTTP request.
        """
        if not body:
            body = MessageUtils.json_payload_to_dict(dxl_request)

        def _handle_request(request_url, body):
            return requests.post(request_url,
                                 headers=self._request_headers,
                                 json=body,
                                 auth=self._request_auth,
                                 verify=self._verify_certificate)

        self._request(dxl_request, path, _handle_request, body)
