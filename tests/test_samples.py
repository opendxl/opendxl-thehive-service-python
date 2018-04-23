from __future__ import absolute_import
import base64
import json
import re
import sys
from tempfile import NamedTemporaryFile
import unittest

if sys.version_info[0] > 2:
    import builtins  # pylint: disable=import-error, unused-import
    from urllib.parse import quote_plus  # pylint: disable=no-name-in-module, import-error, unused-import
else:
    import __builtin__  # pylint: disable=import-error

    builtins = __builtin__  # pylint: disable=invalid-name
    from urllib import quote_plus  # pylint: disable=no-name-in-module, ungrouped-imports

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

# pylint: disable=wrong-import-position
from mock import patch
import requests_mock
import dxlthehiveservice


class StringMatches(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return re.match(self.pattern, other, re.DOTALL)


class StringDoesNotMatch(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return not re.match(self.pattern, other)


class Sample(unittest.TestCase):
    _TEST_HOSTNAME = "127.0.0.1"
    _TEST_API_KEY = "myspecialkey"
    _TEST_API_PORT = "443"
    _TEST_API_USER = "myspecialuser"

    def get_api_endpoint(self, path):
        return "https://" + self._TEST_HOSTNAME + ":" + self._TEST_API_PORT + \
               "/" + path

    @staticmethod
    def expected_print_output(title, detail):
        return_value = title + json.dumps(
            detail, sort_keys=True,
            separators=(".*", ": ")).replace("{", ".*")
        return re.sub(r"[\[}\]]", "", return_value)

    @staticmethod
    def _run_sample(app, sample_file):
        app.run()
        with open(sample_file) as f, \
                patch.object(builtins, 'print') as mock_print:
            sample_globals = {"__file__": sample_file}
            exec(f.read(), sample_globals)  # pylint: disable=exec-used
        return mock_print

    def run_sample(self, sample_file, add_request_mocks_fn=None,
                   api_password=""):
        with dxlthehiveservice.TheHiveService("sample") as app, \
                NamedTemporaryFile(mode="w+") as temp_config_file:
            config = ConfigParser()
            config.read(app._app_config_path)

            use_mock_requests = not config.has_option(
                dxlthehiveservice.TheHiveService._GENERAL_CONFIG_SECTION,
                dxlthehiveservice.TheHiveService._GENERAL_API_PRINCIPAL_CONFIG_PROP
            ) or not config.get(
                dxlthehiveservice.TheHiveService._GENERAL_CONFIG_SECTION,
                dxlthehiveservice.TheHiveService._GENERAL_API_PRINCIPAL_CONFIG_PROP
            )

            if use_mock_requests:
                config.set(
                    dxlthehiveservice.TheHiveService._GENERAL_CONFIG_SECTION,
                    dxlthehiveservice.TheHiveService._GENERAL_HOST_CONFIG_PROP,
                    self._TEST_HOSTNAME
                )
                config.set(
                    dxlthehiveservice.TheHiveService._GENERAL_CONFIG_SECTION,
                    dxlthehiveservice.TheHiveService._GENERAL_PORT_CONFIG_PROP,
                    self._TEST_API_PORT
                )
                config.set(
                    dxlthehiveservice.TheHiveService._GENERAL_CONFIG_SECTION,
                    dxlthehiveservice.TheHiveService._GENERAL_API_PRINCIPAL_CONFIG_PROP,
                    self._TEST_API_KEY
                )
                config.set(
                    dxlthehiveservice.TheHiveService._GENERAL_CONFIG_SECTION,
                    dxlthehiveservice.TheHiveService._GENERAL_API_PASSWORD_CONFIG_PROP,
                    api_password
                )
                config.set(
                    dxlthehiveservice.TheHiveService._GENERAL_CONFIG_SECTION,
                    dxlthehiveservice.TheHiveService._GENERAL_USE_SSL_CONFIG_PROP,
                    "yes"
                )
                config.write(temp_config_file)
                temp_config_file.flush()
                app._app_config_path = temp_config_file.name
                with requests_mock.mock(case_sensitive=True) as req_mock:
                    if add_request_mocks_fn:
                        add_request_mocks_fn(req_mock)
                    mock_print = self._run_sample(app, sample_file)
            else:
                mock_print = self._run_sample(app, sample_file)
                req_mock = None
        return (mock_print, req_mock)

    def test_basic_alert_example(self):
        mock_alert_id = "123456"
        mock_api_password = "mysecretpassword"
        expected_alert_detail = {
            "title": "OpenDXL Alert Example",
            "description": "Created by the OpenDXL Alert Example",
            "severity": 3,
            "source": "OpenDXL",
            "type": "external"
        }

        def add_create_alert_request_mocks(req_mock):
            alert_detail_with_id = expected_alert_detail.copy()
            alert_detail_with_id["id"] = mock_alert_id
            alert_json_with_id = json.dumps(alert_detail_with_id)
            req_mock.post(self.get_api_endpoint("api/alert"),
                          text=alert_json_with_id)
            req_mock.get(
                self.get_api_endpoint("api/alert/{}".format(mock_alert_id)),
                text=alert_json_with_id)

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_create_alert_example.py",
            add_create_alert_request_mocks,
            mock_api_password
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertEqual(2, request_count)

            new_alert_request = req_mock.request_history[0]
            new_alert_request_payload = new_alert_request.json()
            alert_detail_with_source_ref = expected_alert_detail.copy()
            alert_detail_with_source_ref["sourceRef"] = \
                new_alert_request_payload.get("sourceRef", "bogus")
            self.assertEqual(alert_detail_with_source_ref,
                             new_alert_request_payload)

            expected_creds = "Basic {}".format(base64.b64encode(
                "{}:{}".format(self._TEST_API_KEY,
                               mock_api_password).encode("utf8")).decode("utf8"))
            for request in req_mock.request_history:
                self.assertEqual(expected_creds,
                                 request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the create alert request:",
                    expected_alert_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the get alert request:", expected_alert_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

        def add_search_alert_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/alert/_search"),
                          text=json.dumps(expected_alert_detail))

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_search_alert_example.py",
            add_search_alert_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertEqual(1, request_count)

            search_alert_request = req_mock.request_history[0]
            self.assertEqual({
                "query": {"_string": "title:(OpenDXL AND Alert)"},
                "range": "0-1",
                "sort": ["-createdAt"]
            }, search_alert_request.json())

            expected_creds = "Bearer {}".format(self._TEST_API_KEY)
            for request in req_mock.request_history:
                self.assertEqual(expected_creds,
                                 request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the search alert request:",
                    expected_alert_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

    def test_basic_case_task_example(self):
        mock_case_id = "123456"
        mock_task_id = "567890"
        expected_case_detail = {
            "title": "OpenDXL Case Task Example",
            "description": "Created by the OpenDXL Case Task Example",
            "severity": 3
        }
        expected_task_detail = {
            "title": "OpenDXL Case Task Example",
            "description": "Created by the OpenDXL Case Task Example",
            "status": "InProgress",
        }
        mock_case_detail_with_id = expected_case_detail.copy()
        mock_case_detail_with_id["id"] = mock_case_id
        mock_case_json_with_id = json.dumps(mock_case_detail_with_id)

        def add_create_case_task_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/case"),
                          text=mock_case_json_with_id)
            req_mock.get(
                self.get_api_endpoint("api/case/{}".format(mock_case_id)),
                text=mock_case_json_with_id)
            task_detail_with_id = expected_task_detail.copy()
            task_detail_with_id["id"] = mock_task_id
            task_json_with_id = json.dumps(task_detail_with_id)
            req_mock.post(self.get_api_endpoint(
                "api/case/{}/task".format(
                    mock_case_id)), text=task_json_with_id)
            req_mock.get(
                self.get_api_endpoint("api/case/task/{}".format(mock_task_id)),
                text=task_json_with_id)

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_create_case_task_example.py",
            add_create_case_task_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertEqual(4, request_count)

            new_case_request = req_mock.request_history[0]
            self.assertEqual(expected_case_detail, new_case_request.json())

            new_case_task_request = req_mock.request_history[2]
            self.assertEqual(expected_task_detail, new_case_task_request.json())

            expected_creds = "Bearer {}".format(self._TEST_API_KEY)
            for request in req_mock.request_history:
                self.assertEqual(expected_creds,
                                 request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the create case request:",
                    expected_case_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the get case request:",
                    expected_case_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the create case task request:",
                    expected_task_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the get case task request:",
                    expected_task_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

        def search_case_task_request_mocks(req_mock):
            task_detail_with_id = expected_task_detail.copy()
            task_detail_with_id["id"] = mock_task_id
            task_json_with_id = json.dumps(task_detail_with_id)
            req_mock.post(self.get_api_endpoint("api/case/_search"),
                          text=json.dumps([mock_case_detail_with_id]))
            req_mock.post(self.get_api_endpoint("api/case/task/_search"),
                          text=task_json_with_id)

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_search_case_task_example.py",
            search_case_task_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertEqual(2, request_count)

            search_case_request = req_mock.request_history[0]
            self.assertEqual({
                "query": {"_string": "title:(OpenDXL AND Task)"},
                "range": "0-1"
            }, search_case_request.json())

            search_case_task_request = req_mock.request_history[1]
            self.assertEqual({
                "query": {"_parent": {"_type": "case",
                                      "_query": {"_id": mock_case_id}}}
            }, search_case_task_request.json())

            expected_creds = "Bearer {}".format(self._TEST_API_KEY)
            for request in req_mock.request_history:
                self.assertEqual(expected_creds,
                                 request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the search case request:",
                    expected_case_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the search case task request:",
                    expected_task_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

    def test_basic_case_observable_example(self):
        mock_case_id = "123456"
        mock_observable_id = "567890"
        expected_case_detail = {
            "title": "OpenDXL Case Observable Example",
            "description": "Created by the OpenDXL Case Observable Example",
            "severity": 3
        }
        expected_observable_detail = {
            "data": "OpenDXL",
            "message": "Created by the OpenDXL Case Observable Example",
            "dataType": "user-agent",
        }
        mock_case_detail_with_id = expected_case_detail.copy()
        mock_case_detail_with_id["id"] = mock_case_id
        mock_case_json_with_id = json.dumps(mock_case_detail_with_id)

        def add_create_case_observable_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/case"),
                          text=mock_case_json_with_id)
            req_mock.get(
                self.get_api_endpoint("api/case/{}".format(mock_case_id)),
                text=mock_case_json_with_id)
            observable_detail_with_id = expected_observable_detail.copy()
            observable_detail_with_id["id"] = mock_observable_id
            observable_json_with_id = json.dumps(observable_detail_with_id)
            req_mock.post(
                self.get_api_endpoint(
                    "api/case/{}/artifact".format(mock_case_id)),
                text=observable_json_with_id)
            req_mock.get(
                self.get_api_endpoint("api/case/artifact/{}".format(
                    mock_observable_id)),
                text=observable_json_with_id)

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_create_case_observable_example.py",
            add_create_case_observable_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertEqual(4, request_count)

            new_case_request = req_mock.request_history[0]
            self.assertEqual(expected_case_detail, new_case_request.json())

            new_case_observable_request = req_mock.request_history[2]
            self.assertEqual(expected_observable_detail,
                             new_case_observable_request.json())

            expected_creds = "Bearer {}".format(self._TEST_API_KEY)
            for request in req_mock.request_history:
                self.assertEqual(expected_creds,
                                 request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the create case request:",
                    expected_case_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the get case request:",
                    expected_case_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the create case observable request:",
                    expected_observable_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the get case observable request:",
                    expected_observable_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

        def search_case_observable_request_mocks(req_mock):
            observable_detail_with_id = expected_observable_detail.copy()
            observable_detail_with_id["id"] = mock_observable_id
            task_observable_with_id = json.dumps(observable_detail_with_id)
            req_mock.post(self.get_api_endpoint("api/case/_search"),
                          text=json.dumps([mock_case_detail_with_id]))
            req_mock.post(self.get_api_endpoint("api/case/artifact/_search"),
                          text=task_observable_with_id)

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_search_case_observable_example.py",
            search_case_observable_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertEqual(2, request_count)

            search_case_request = req_mock.request_history[0]
            self.assertEqual({
                "query": {"_string": "title:(OpenDXL AND Observable)"},
                "range": "0-1"
            }, search_case_request.json())

            search_case_observable_request = req_mock.request_history[1]
            self.assertEqual({
                "query": {"_parent": {"_type": "case",
                                      "_query": {"_id": mock_case_id}}}
            }, search_case_observable_request.json())

            expected_creds = "Bearer {}".format(self._TEST_API_KEY)
            for request in req_mock.request_history:
                self.assertEqual(expected_creds,
                                 request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the search case request:",
                    expected_case_detail
                )
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response for the search case observable request:",
                    expected_observable_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))
