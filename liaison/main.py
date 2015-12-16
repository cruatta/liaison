from __future__ import absolute_import

from liaison import log
from liaison.sink import Sink
from liaison.consul import Consul

import multiprocessing
import time

class Liaison(object):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def create_pool(config):
        """

        :param config: LiaisonConfig object
        :type config: LiaisonConfig

        :return pool, pool_size: A multiprocessing pool and the size
        the pool should be.
        :rtype: multiprocessing.Pool, int
        """
        if config.pool_size is None:
            pool_size = multiprocessing.cpu_count()
        else:
            pool_size = config.pool_size

        pool = multiprocessing.Pool(pool_size)

        return pool, pool_size

    def create_check_service_jobs(self, services):
        """

        :param services: A dict of services and tags
        :type services: dict

        :return: A list of check service jobs
        :rtype: dict
        """
        check_service_jobs = list()
        for name, tags in services.iteritems():
            for tag in tags:
                check_service_jobs.append(
                    {'service': name, 'tag': tag,
                     'consul_config': self.config.consul_config,
                     'sink_config': self.config.sink_config})

            check_service_jobs.append(
                {'service': name, 'tag': None,
                 'consul_config': self.config.consul_config,
                 'sink_config': self.config.sink_config})

        return check_service_jobs

    def loop(self):
        """
        The main read loop.
        """

        consul_config = self.config.consul_config
        consul = Consul(consul_config)

        services = consul.get_services()
        check_service_jobs = self.create_check_service_jobs(services)

        pool, pool_size = self.create_pool(self.config)

        while len(check_service_jobs) > 0:
            if len(check_service_jobs) >= pool_size:
                pool.map(check_service,
                         [check_service_jobs.pop()
                          for _ in range(pool_size)])
            else:
                pool.map(check_service,
                         [check_service_jobs.pop()
                          for _ in range(len(check_service_jobs))])

            time.sleep(self.config.sleep)

        pool.close()
        pool.join()

def check_service(check_service_job):
    """
    Check the availability of a consul service and send stats to a Sink.

    :param check_service_job: Dictionary containing job specification
    :type check_service_job: dict[str, str, ConsulConfig, SinkConfig]

    :return: Integer return code
    :rtype: int
    """

    try:
        service = check_service_job['service']
        tag = check_service_job['tag']
        consul_config = check_service_job['consul_config']
        sink_config = check_service_job['sink_config']
    except KeyError as e:
        log.error("Missing key {e} in check_service_job".format(e=e))
        return 2

    consul = Consul(consul_config)
    sink = Sink(sink_config)

    dc = consul.get_dc()
    log.debug('Running service availability check on '
              'Service:{service} Tag:{tag} DC:{dc}'.format(service=service,
                                                           tag=tag, dc=dc))

    consul_health_service = consul.get_health_service(service, tag)
    ok, critical = get_node_status(consul_health_service)

    sink.ok_count(ok, service, dc, tag)
    sink.critical_count(critical, service, dc, tag)

    if ok + critical > 0:
        sink.ok_percent(float((ok / (ok + critical))), service, dc, tag)
        sink.critical_percent(float((critical / (ok + critical))),
                              service, dc, tag)

    return 0


def get_node_status(consul_health_service):
    """

    :param consul_health_service: A dictionary of representation
    of the result of a query to /v1/health/service/<service>
    :type consul_health_service: dict

    :return: number of nodes without critical checks,
        number of nodes with critical checks
    :rtype: int, int
    """
    nodes = dict()
    ok = 0
    critical = 0

    for node in consul_health_service:
        name = node['Node']['Node']

        if name not in nodes:
            nodes[name] = dict()
            nodes[name]['passing'] = 0
            nodes[name]['warning'] = 0
            nodes[name]['critical'] = 0

        for check in node['Checks']:
            if check['Status'] == 'passing':
                nodes[name]['passing'] += 1
            elif check['Status'] == 'warning':
                nodes[name]['warning'] += 1
            elif check['Status'] == 'critical':
                nodes[name]['critical'] += 1
            else:
                continue

        if nodes[name]['critical'] > 0:
            critical += 1
        else:
            ok += 1

    return ok, critical
