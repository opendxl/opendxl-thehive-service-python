from __future__ import absolute_import
import base64
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

    def run_sample(self, sample_file, add_request_mocks_fn=None,
                   api_password=""):
        sample_globals = {"__file__": sample_file}
        with requests_mock.mock(case_sensitive=True) as req_mock, \
                dxlthehiveservice.TheHiveService("sample") as app, \
                NamedTemporaryFile(mode="w+") as temp_config_file:
            config = ConfigParser()
            config.read(app._app_config_path)
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
            if add_request_mocks_fn:
                add_request_mocks_fn(req_mock)
            app.run()
            with open(sample_file) as f, \
                    patch.object(builtins, 'print') as mock_print:
                exec(f.read(), sample_globals)  # pylint: disable=exec-used
        return (mock_print, req_mock)

    def test_basic_create_alert_example(self):
        alert_id = "123456"
        api_password = "mysecretpassword"

        def add_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/alert"),
                          text='{"id": "' + alert_id + '"}')
            req_mock.get(
                self.get_api_endpoint("api/alert/{}".format(alert_id)),
                text='{"response": "got the new alert"}')

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_create_alert_example.py",
            add_request_mocks,
            api_password
        )

        request_count = len(req_mock.request_history)
        self.assertEqual(2, request_count)

        new_alert_request = req_mock.request_history[0]
        new_alert_request_payload = new_alert_request.json()
        self.assertEqual({
            "title": "OpenDXL Alert Example",
            "description": "Created by the OpenDXL Alert Example",
            "severity": 3,
            "source": "OpenDXL",
            "sourceRef": new_alert_request_payload.get("sourceRef", "bogus"),
            "type": "external"
        }, new_alert_request_payload)

        expected_creds = "Basic {}".format(base64.b64encode(
            "{}:{}".format(self._TEST_API_KEY,
                           api_password).encode("utf8")).decode("utf8"))
        for request in req_mock.request_history:
            self.assertEqual(expected_creds, request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                "Response for the create alert request:.*id.*" + alert_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the get alert request:.*got the new alert"
            ))
        mock_print.assert_any_call(
            StringDoesNotMatch("Error invoking request"))

    def test_basic_create_case_task_example(self):
        case_id = "123456"
        task_id = "567890"

        def add_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/case"),
                          text='{"id": "' + case_id + '"}')
            req_mock.get(self.get_api_endpoint("api/case/{}".format(case_id)),
                         text='{"response": "got the new case"}')
            req_mock.post(self.get_api_endpoint(
                "api/case/{}/task".format(case_id)
                ), text='{"id": "' + task_id + '"}')
            req_mock.get(
                self.get_api_endpoint("api/case/task/{}".format(task_id)),
                text='{"response": "got the new task"}')

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_create_case_task_example.py",
            add_request_mocks
        )

        request_count = len(req_mock.request_history)
        self.assertEqual(4, request_count)

        new_case_request = req_mock.request_history[0]
        self.assertEqual({
            "title": "OpenDXL Case Task Example",
            "description": "Created by the OpenDXL Case Task Example",
            "severity": 3,
        }, new_case_request.json())

        new_case_task_request = req_mock.request_history[2]
        self.assertEqual({
            "title": "OpenDXL Case Task Example",
            "description": "Created by the OpenDXL Case Task Example",
            "status": "InProgress",
        }, new_case_task_request.json())

        expected_creds = "Bearer {}".format(self._TEST_API_KEY)
        for request in req_mock.request_history:
            self.assertEqual(expected_creds, request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                "Response for the create case request:.*id.*" + case_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the get case request:.*got the new case"
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the create case task request:.*id.*" + task_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the get case task request:.*got the new task"
            ))
        mock_print.assert_any_call(
            StringDoesNotMatch("Error invoking request"))

    def test_basic_create_case_observable_example(self):
        case_id = "123456"
        observable_id = "567890"

        def add_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/case"),
                          text='{"id": "' + case_id + '"}')
            req_mock.get(self.get_api_endpoint("api/case/{}".format(case_id)),
                         text='{"response": "got the new case"}')
            req_mock.post(
                self.get_api_endpoint("api/case/{}/artifact".format(case_id)),
                text='{"id": "' + observable_id + '"}')
            req_mock.get(self.get_api_endpoint(
                "api/case/artifact/{}".format(observable_id)),
                         text='{"response": "got the new observable"}')

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_create_case_observable_example.py",
            add_request_mocks
        )

        request_count = len(req_mock.request_history)
        self.assertEqual(4, request_count)

        new_case_request = req_mock.request_history[0]
        self.assertEqual({
            "title": "OpenDXL Case Observable Example",
            "description": "Created by the OpenDXL Case Observable Example",
            "severity": 3,
        }, new_case_request.json())

        new_case_observable_request = req_mock.request_history[2]
        self.assertEqual({
            "data": "OpenDXL",
            "message": "Created by the OpenDXL Case Observable Example",
            "dataType": "user-agent",
        }, new_case_observable_request.json())

        expected_creds = "Bearer {}".format(self._TEST_API_KEY)
        for request in req_mock.request_history:
            self.assertEqual(expected_creds, request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                "Response for the create case request:.*id.*" + case_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the get case request:.*got the new case"
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the create case observable request:.*id.*" +
                observable_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the get case observable request:" +
                ".*got the new observable"
            ))
        mock_print.assert_any_call(
            StringDoesNotMatch("Error invoking request"))

    def test_basic_search_alert_example(self):
        def add_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/alert/_search"),
                          text='[{"response": "found an alert"}]')

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_search_alert_example.py",
            add_request_mocks
        )

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
            self.assertEqual(expected_creds, request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                "Response for the search alert request:" +
                ".*response.*found an alert"
            ))
        mock_print.assert_any_call(
            StringDoesNotMatch("Error invoking request"))

    def test_basic_search_case_task_example(self):
        case_id = "123456"

        def add_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/case/_search"),
                          text='[{"id": "' + case_id + '"}]')
            req_mock.post(self.get_api_endpoint("api/case/task/_search"),
                          text='[{"response": "found task"}]')

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_search_case_task_example.py",
            add_request_mocks
        )

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
                                  "_query": {"_id": case_id}}}
        }, search_case_task_request.json())

        expected_creds = "Bearer {}".format(self._TEST_API_KEY)
        for request in req_mock.request_history:
            self.assertEqual(expected_creds, request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                "Response for the search case request:.*id.*" + case_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the search case task request:" +
                ".*response.*found task"
            ))
        mock_print.assert_any_call(
            StringDoesNotMatch("Error invoking request"))

    def test_basic_search_case_observable_example(self):
        observable_id = "123456"

        def add_request_mocks(req_mock):
            req_mock.post(self.get_api_endpoint("api/case/_search"),
                          text='[{"id": "' + observable_id + '"}]')
            req_mock.post(self.get_api_endpoint("api/case/artifact/_search"),
                          text='[{"response": "found observable"}]')

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_search_case_observable_example.py",
            add_request_mocks
        )

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
                                  "_query": {"_id": observable_id}}}
        }, search_case_observable_request.json())

        expected_creds = "Bearer {}".format(self._TEST_API_KEY)
        for request in req_mock.request_history:
            self.assertEqual(expected_creds, request.headers["Authorization"])

        mock_print.assert_any_call(
            StringMatches(
                "Response for the search case request:.*id.*" + observable_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response for the search case observable request:" +
                ".*response.*found observable"
            ))
        mock_print.assert_any_call(
            StringDoesNotMatch("Error invoking request"))
