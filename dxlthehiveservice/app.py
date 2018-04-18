from __future__ import absolute_import
import logging
import os

from dxlbootstrap.app import Application
from dxlclient.service import ServiceRegistrationInfo
from .requesthandlers import *
from .thehive_client import TheHiveClient

# Configure local logger
logger = logging.getLogger(__name__)


class TheHiveService(Application):
    """
    The "TheHive DXL Service" application class.
    """

    #: The service type for TheHive service API.
    _SERVICE_TYPE = "/opendxl-thehive/service/thehive-api"

    #: The name of the "General" section within the application configuration
    #: file.
    _GENERAL_CONFIG_SECTION = "General"
    #: The property used to specify a unique service discriminator to the
    #: application configuration file. The discriminator, if set, is added to
    #: each of TheHive API topics registered with the DXL fabric.
    _GENERAL_SERVICE_UNIQUE_ID_PROP = "serviceUniqueId"
    #: The property used to specify the hostname or IP address of TheHive
    #: server in the application configuration file.
    _GENERAL_HOST_CONFIG_PROP = "host"
    #: The property used to specify the port number of TheHive API server in
    #: the application configuration file.
    _GENERAL_PORT_CONFIG_PROP = "port"
    #: The property used to specify in the application configuration file
    #: whether or not SSL/TLS should be used when communicating with an
    #: TheHive server.
    _GENERAL_USE_SSL_CONFIG_PROP = "useSSL"
    #: The property used to specify the list of accessible TheHive APIs in the
    #: application configuration file
    _GENERAL_API_NAMES_CONFIG_PROP = "apiNames"
    #: The property used to specify TheHive API principal in the application
    #: configuration file.
    _GENERAL_API_PRINCIPAL_CONFIG_PROP = "apiPrincipal"
    #: The property used to specify TheHive API password in the application
    #: configuration file.
    _GENERAL_API_PASSWORD_CONFIG_PROP = "apiPassword"
    #: The property used to specify in the application configuration file
    #: whether or not TheHive server certificate was signed by a valid
    #: certificate authority.
    _GENERAL_VERIFY_CERTIFICATE_CONFIG_PROP = "verifyCertificate"
    #: The property used to specify in the application configuration file
    #: a path to a bundle of trusted CA certificates to use for validating
    #: TheHive server's certificate.
    _GENERAL_VERIFY_CERT_BUNDLE_CONFIG_PROP = "verifyCertBundle"

    #: Default plaintext HTTP port number at which TheHive API server is
    #: expected to be hosted.
    _DEFAULT_HTTP_PORT = 9000
    #: Default plaintext HTTPS port number at which TheHive API server is
    #: expected to be hosted.
    _DEFAULT_HTTPS_PORT = 9443
    #: Default for whether or not TheHive server is expected to be hosted
    #: under SSL/TLS.
    _DEFAULT_USE_SSL = True

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the
            application
        """
        super(TheHiveService, self).__init__(config_dir,
                                             "dxlthehiveservice.config")
        self._service_unique_id = None
        self._api_names = None
        self._api_principal = None
        self._api_password = None
        self._api_url = None
        self._verify_certificate = None

    @property
    def client(self):
        """
        The DXL client used by the application to communicate with the DXL
        fabric
        """
        return self._dxl_client

    @property
    def config(self):
        """
        The application configuration (as read from the "dxlthehiveservice.config" file)
        """
        return self._config

    def on_run(self):
        """
        Invoked when the application has started running.
        """
        logger.info("On 'run' callback.")

    def _get_setting_from_config(self, section, setting,
                                 default_value=None,
                                 return_type=str,
                                 raise_exception_if_missing=False,
                                 is_file_path=False):
        """
        Get the value for a setting in the application configuration file.

        :param str section: Name of the section in which the setting resides.
        :param str setting: Name of the setting.
        :param default_value: Value to return if the setting is not found in
            the configuration file.
        :param type return_type: Expected 'type' of the value to return.
        :param bool raise_exception_if_missing: Whether or not to raise an
            exception if the setting is missing from the configuration file.
        :param bool is_file_path: Whether or not the value for the setting
            represents a file path. If set to 'True' but a file cannot be
            found for the setting, a ValueError is raised.
        :return: Value for the setting.
        :raises ValueError: If the setting cannot be found in the configuration
            file and 'raise_exception_if_missing' is set to 'True', the
            type of the setting found in the configuration file does not
            match the value specified for 'return_type', or 'is_file_path' is
            set to 'True' but no file can be found which matches the value
            read for the setting.
        """
        config = self.config
        if config.has_option(section, setting):
            getter_methods = {str: config.get,
                              list: config.get,
                              bool: config.getboolean,
                              int: config.getint,
                              float: config.getfloat}
            try:
                return_value = getter_methods[return_type](section, setting)
            except ValueError as ex:
                raise ValueError(
                    "Unexpected value for setting {} in section {}: {}".format(
                        setting, section, ex))
            if return_type == str:
                return_value = return_value.strip()
                if len(return_value) is 0 and raise_exception_if_missing:
                    raise ValueError(
                        "Required setting {} in section {} is empty".format(
                            setting, section))
            elif return_type == list:
                return_value = [item.strip()
                                for item in return_value.split(",")]
                if len(return_value) is 1 and len(return_value[0]) is 0 \
                        and raise_exception_if_missing:
                    raise ValueError(
                        "Required setting {} in section {} is empty".format(
                            setting, section))
        elif raise_exception_if_missing:
            raise ValueError(
                "Required setting {} not found in {} section".format(setting,
                                                                     section))
        else:
            return_value = default_value

        if is_file_path and return_value:
            return_value = self._get_path(return_value)
            if not os.path.isfile(return_value):
                raise ValueError(
                    "Cannot find file for setting {} in section {}: {}".format(
                        setting, section, return_value))

        return return_value

    def on_load_configuration(self, config):
        """
        Invoked after the application-specific configuration has been loaded

        This callback provides the opportunity for the application to parse
        additional configuration properties.

        :param config: The application configuration
        """
        logger.info("On 'load configuration' callback.")

        self._service_unique_id = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_SERVICE_UNIQUE_ID_PROP)

        host = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_HOST_CONFIG_PROP,
            raise_exception_if_missing=True)

        use_ssl = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_USE_SSL_CONFIG_PROP,
            return_type=bool,
            default_value=self._DEFAULT_USE_SSL
        )

        port = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_PORT_CONFIG_PROP,
            return_type=int,
            default_value=self._DEFAULT_HTTPS_PORT \
                if use_ssl else self._DEFAULT_HTTP_PORT)

        self._api_url = "http{}://{}:{}".format(
            "s" if use_ssl else "", host, port)

        self._api_names = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_API_NAMES_CONFIG_PROP,
            return_type=list,
            raise_exception_if_missing=True)

        self._api_principal = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_API_PRINCIPAL_CONFIG_PROP,
            raise_exception_if_missing=True)

        self._api_password = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_API_PASSWORD_CONFIG_PROP,
        )

        verify_certificate = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_VERIFY_CERTIFICATE_CONFIG_PROP,
            return_type=bool,
            default_value=True
        )
        if verify_certificate:
            verify_cert_bundle = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_VERIFY_CERT_BUNDLE_CONFIG_PROP,
                is_file_path=True
            )
            if verify_cert_bundle:
                verify_certificate = verify_cert_bundle
        self._verify_certificate = verify_certificate

    def on_dxl_connect(self):
        """
        Invoked after the client associated with the application has connected
        to the DXL fabric.
        """
        logger.info("On 'DXL connect' callback.")

    def on_register_services(self):
        """
        Invoked when services should be registered with the application
        """
        callbacks = {
            "create_case": TheHiveCreateCaseRequestCallback,
            "create_case_task": TheHiveCreateCaseTaskRequestCallback,
            "create_case_observable": TheHiveCreateCaseObservableRequestCallback,
            "get_case": TheHiveGetCaseRequestCallback,
            "get_case_task": TheHiveGetCaseTaskRequestCallback,
            "get_case_observable": TheHiveGetCaseObservableRequestCallback,
            "search_case": TheHiveSearchCaseRequestCallback,
            "search_case_task": TheHiveSearchCaseTaskRequestCallback,
            "search_case_observable": TheHiveSearchCaseObservableRequestCallback,
            "create_alert": TheHiveCreateAlertRequestCallback,
            "get_alert": TheHiveGetAlertRequestCallback,
            "search_alert": TheHiveSearchAlertRequestCallback
        }

        # Register service 'thehive_service'
        logger.info("Registering service: %s", "thehive_service")
        service = ServiceRegistrationInfo(self._dxl_client, self._SERVICE_TYPE)

        logger.info("Connecting to API URL: %s", self._api_url)
        thehive_client = TheHiveClient(self._dxl_client,
                                       self._api_url,
                                       self._api_principal,
                                       self._api_password,
                                       self._verify_certificate)

        for api_name in self._api_names:
            api_method = callbacks.get(api_name, None)
            if api_method:
                topic_name_end, _, topic_name_start = api_name.partition("_")
                topic_name = "{}{}/{}/{}".format(
                    self._SERVICE_TYPE,
                    "/{}".format(self._service_unique_id) \
                    if self._service_unique_id else "",
                    topic_name_start.replace("_", "/"),
                    topic_name_end)
                logger.info(
                    "Registering request callback: thehive_%s_requesthandler",
                    api_name)
                self.add_request_callback(
                    service, topic_name,
                    api_method(self._dxl_client, thehive_client),
                    False)
            else:
                logger.warning("API name is invalid: %s", api_name)

        self.register_service(service)
