from __future__ import absolute_import
from liaison.config import ConsulConfig
from consul import Consul as ConsulAPI


class Consul(object):
    def __init__(self, config):
        """

        :param config:
        :type config: ConsulConfig
        """
        self.api = ConsulAPI(**config.kwargs())

    def get_dc(self):
        """

        :return: The datacenter specified for use by the API
        :rtype: str
        """
        return self.api.dc

    def get_services(self):
        """

        :return: A dictionary of services and tags
        :rtype: dict
        """
        _, services = self.api.catalog.services()
        return services

    def get_health_service(self, service, tag=None):
        """

        :param service: The name of the consul service
        :type service: str
        :param tag: A tag for the service
        :type tag: str|None

        :return: A list of representation of the result of
        a query to /v1/health/service/<service>
        :rtype: list

        """
        if tag:
            _, health_service = self.api.health.service(service, tag=tag)
        else:
            _, health_service = self.api.health.service(service)

        return health_service
