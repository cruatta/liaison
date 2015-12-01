from copy import deepcopy

class LiaisonConfig(object):
    def __init__(self, pool_size=4, pause_time=30):
        self.pool_size = pool_size
        self.pause_time = pause_time


class ConsulConfig(object):
    def __init__(self, host='127.0.0.1', port=8500,
                 token=None, scheme='http',
                 consistency='default',
                 dc=None, verify=True):
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
    def __init__(self, host='127.0.0.1', port=8125):
        self.host = host
        self.port = port

    def args(self):
        return [self.host, self.port]

