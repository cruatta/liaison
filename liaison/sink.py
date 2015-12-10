import statsd
import log
from config import SinkConfig, StatsdOptions


class StatsdSink(object):

    def __init__(self, options):
        """
        :param options: Statsd configuration options
        :type options: StatsdOptions
        """
        self.s = statsd.StatsClient(*options.args())

    def ok_count(self, value, service, dc, tag):
        if tag:
            self.s.gauge('consul.service.{dc}.{srv}.{tag}.ok.count'.format(
                srv=service, tag=tag, dc=dc), value)
        else:
            self.s.gauge('consul.service.{dc}.{srv}.ok.count'.format(
                srv=service, dc=dc), value)

    def critical_count(self, value, service, dc, tag):
        if tag:
            self.s.gauge('consul.service.{dc}.{srv}.{tag}.critical.count'.format(
                srv=service, tag=tag, dc=dc), value)
        else:
            self.s.gauge('consul.service.{dc}.{srv}.critical.count'.format(
                srv=service, dc=dc), value)

    def ok_percent(self, value, service, dc, tag):
        if tag:
            self.s.gauge('consul.service.{dc}.{srv}.{tag}.ok.percent'.format(
                srv=service, tag=tag, dc=dc), value)
        else:
            self.s.gauge('consul.service.{dc}.{srv}.ok.percent'.format(
                srv=service, dc=dc), value)

    def critical_percent(self, value, service, dc, tag):
        if tag:
            self.s.gauge('consul.service.{dc}.{srv}.{tag}.critical.percent'.format(
                srv=service, tag=tag, dc=dc), value)
        else:
            self.s.gauge('consul.service.{dc}.{srv}.critical.percent'.format(
                srv=service, dc=dc), value)


class Sink(object):
    def __init__(self, config):
        """
        :param config:
        :type config: SinkConfig
        :return:
        """

        self.config = config
        if self.config.type == 'statsd':
            self.sink = StatsdSink(self.config.opts)
        else:
            log.critical("Invalid Sink type")
            raise Exception("Invalid Sink type")

    def ok_count(self, value, service, dc, tag):
        self.sink.ok_count(value, service, dc, tag)

    def ok_percent(self, value, service, dc, tag):
        self.sink.ok_percent(value, service, dc, tag)

    def critical_count(self, value, service, dc, tag):
        self.sink.critical_count(value, service, dc, tag)

    def critical_percent(self, value, service, dc, tag):
        self.sink.critical_percent(value, service, dc, tag)
