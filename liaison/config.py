class LiaisonConfig(object):
    """
    Configuration object for Liaison.
    """
    def __init__(self, pool_size=4, sleep=30):
        """
        :param pool_size: Number of checks to run in parallel
        :type pool_size: int

        :param sleep: Time to sleep between checks in the main loop in seconds
        :type sleep: float
        """
        self.pool_size = pool_size
        self.sleep = sleep


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
        return self.__dict__

class StatsdConfig(object):
    """
    Configuration object for StatsD.
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
        return [self.host, self.port]

