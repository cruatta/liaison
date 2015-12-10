import json
import log
import sys

class LiaisonConfig(object):
    """
    Configuration object for the Liaison app itself.
    """
    def __init__(self, pool_size=1, sleep=1, consul_config=None,
                 sink_config=None):
        """
        :param pool_size: Number of checks to run in parallel
        :type pool_size: int

        :param sleep: Time to sleep between checks in the main loop in seconds
        :type sleep: float

        :param consul_config: Consul Configuration object
        :type consul_config: ConsulConfig

        :param sink_config: Sink Configuration object
        :type sink_config: SinkConfig
        """
        self.pool_size = pool_size
        self.sleep = sleep

        if consul_config is type(ConsulConfig):
            self.consul_config = consul_config
        else:
            self.consul_config = ConsulConfig()

        if sink_config is type(SinkConfig):
            self.sink_config = sink_config
        else:
            self.sink_config = SinkConfig()


class ConsulConfig(object):
    """
    Configuration object for Consul.
    """
    def __init__(self, host='127.0.0.1', port=8500,
                 token=None, scheme='http',
                 consistency='default',
                 dc=None, verify=True):
        """
        :param host: Consul agent host
        :type host: str

        :param port: Consul HTTP port
        :type port: int

        :param token: An optional string token for Consul ACL
        :type token: str|None

        :param scheme: http or https
        :type scheme: str

        :param consistency: Either default, stale, or consistent
        :type consistency: str

        :param dc: Consul datacenter to use for requests
        :type dc: str|None

        :param verify: Verify HTTPS requests
        :type dc: bool
        """
        self.host = host
        self.port = port
        self.token = token
        self.scheme = scheme
        self.consistency = consistency
        self.dc = dc
        self.verify = verify

    def kwargs(self):
        """
        :return Dictionary of consul configuration
        :rtype: dict
        """
        return self.__dict__


class SinkConfig(object):
    """
    Configuration object for Base Metrics Sink

    :param type: Sink type (eg statsd)
    :type type: str

    :param options: Sink configuration
    :type options: dict
    """
    def __init__(self, type="statsd", options=None):
        self.type = type
        if self.type == "statsd":
            if not options:
                self.opts = StatsdOptions()
            else:
                self.opts = StatsdOptions(**options)
        else:
            log.critical("Invalid Sink configuration.")
            raise Exception("Invalid Sink configuration.")

class StatsdOptions(object):
    """
    Configuration object for StatsD Sink.
    """
    def __init__(self, host='127.0.0.1', port=8125):
        """

        :param host: StatsD host
        :type host: str

        :param port: StatsD port
        :type port: int
        """
        self.host = host
        self.port = port

    def args(self):
        """
        :return: List of host and port for statsd
        :rtype: [str, int]

        """
        return [self.host, self.port]


def load_config(path):
    """
    :param path: Path to configuration file
    :type path: str

    :return: A LiaisonConfig object
    :rtype: LiaisonConfig
    """
    with open(path) as f:
        config = json.load(f)

    pool_size = config['pool_size']
    sleep = config['sleep']
    consul_config = ConsulConfig(**config['consul'])
    sink_config = SinkConfig(**config['sink'])

    lc = LiaisonConfig(pool_size=pool_size,
                       sleep=sleep,
                       consul_config=consul_config,
                       sink_config=sink_config)

    return lc
