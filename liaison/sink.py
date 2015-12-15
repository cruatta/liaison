import statsd
import log


class StatsdSink(object):

    def __init__(self, options):
        """
        :param options: Statsd configuration options
        :type options: StatsdOptions
        """
        self.client = statsd.StatsClient(*options.args())

    def ok_count(self, value, service, dc, tag):
        """

        :param value: Number of "ok" (no critical checks) services
        :type value: int

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        if tag:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.{tag}.ok.count'.format(
                    srv=service, tag=tag, dc=dc), value)
        else:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.ok.count'.format(
                    srv=service, dc=dc), value)

    def critical_count(self, value, service, dc, tag):
        """

        :param value: Number of "critical" (any critical checks) services
        :type value: int

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        if tag:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.{tag}.critical.count'.format(
                    srv=service, tag=tag, dc=dc), value)
        else:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.critical.count'.format(
                    srv=service, dc=dc), value)

    def ok_percent(self, value, service, dc, tag):
        """

        :param value: Percent of "ok" (no critical checks) services
        out of all instances of services
        :type value: float

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        if tag:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.{tag}.ok.percent'.format(
                    srv=service, tag=tag, dc=dc), value)
        else:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.ok.percent'.format(
                    srv=service, dc=dc), value)

    def critical_percent(self, value, service, dc, tag):
        """

        :param value: Percent of "critical" (any critical checks) services
        out of all instances of services
        :type value: float

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        if tag:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.{tag}.critical.percent'.format(
                    srv=service, tag=tag, dc=dc), value)
        else:
            return self.client.gauge(
                'consul.service.{dc}.{srv}.critical.percent'.format(
                    srv=service, dc=dc), value)


class Sink(object):
    def __init__(self, config):
        """
        :param config: A SinkConfig object
        :type config: SinkConfig
        """

        self.config = config
        if self.config.type == 'statsd':
            self.sink = StatsdSink(self.config.opts)
        else:
            log.critical("Invalid Sink type.")
            raise SinkException("Invalid Sink type.")

    def ok_count(self, value, service, dc, tag):
        """

        :param value: Number of "ok" (no critical checks) services
        :type value: int

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        return self.sink.ok_count(value, service, dc, tag)

    def ok_percent(self, value, service, dc, tag):
        """

        :param value: Percent of "ok" (no critical checks) services
        out of all instances of services
        :type value: float

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        return self.sink.ok_percent(value, service, dc, tag)

    def critical_count(self, value, service, dc, tag):
        """

        :param value: Number of "critical" (any critical checks) services
        :type value: int

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        return self.sink.critical_count(value, service, dc, tag)

    def critical_percent(self, value, service, dc, tag):
        """

        :param value: Percent of "critical" (any critical checks) services
        out of all instances of services
        :type value: float

        :param service: Name of the service
        :type service: str

        :param dc: Name of the datacenter
        :type dc: str

        :param tag: Optional tag for the service
        :type tag: str|None

        """
        return self.sink.critical_percent(value, service, dc, tag)


class SinkException(Exception):
    pass
