import log
from sink import Sink
from consul import Consul
import multiprocessing
import time


def create_pool(liaison_config):
    """

    :param liaison_config: LiaisonConfig object
    :type liaison_config: LiaisonConfig

    :return pool, pool_size: A multiprocessing pool and the size
    the pool should be.
    :rtype: multiprocessing.Pool, int
    """
    if liaison_config.pool_size is None:
        pool_size = multiprocessing.cpu_count()
    else:
        pool_size = liaison_config.pool_size

    pool = multiprocessing.Pool(pool_size)

    return pool, pool_size


def create_check_service_jobs(services, consul_config, sink_config):
    """

    :param services: A dict of services and tags
    :type services: dict
    :param consul_config: Consul Config
    :type consul_config: ConsulConfig
    :param sink_config: Sink Config
    :type sink_config: SinkConfig

    :return: A list of check service jobs
    :rtype: dict
    """
    check_service_jobs = list()
    for name, tags in services.iteritems():
        for tag in tags:
            check_service_jobs.append({'service': name, 'tag': tag,
                                       'consul_config': consul_config,
                                       'sink_config': sink_config})
        check_service_jobs.append({'service': name, 'tag': None,
                                   'consul_config': consul_config,
                                   'sink_config': sink_config})
    return check_service_jobs


def get_dc(consul_agent):
    """

    :param consul_agent: A Consul object
    :type consul_agent: Consul

    :return: The datacenter of the agent
    :rtype: str
    """
    self = consul_agent.agent.self()
    dc = self['Config']['Datacenter']
    return dc

def get_services(consul_agent):
    """

    :param consul_agent: A Consul object
    :type consul_agent: Consul

    :return: A dictionary of services and tags
    :rtype: dict
    """
    _, services = consul_agent.catalog.services()
    return services


def get_health_service(consul_agent, service, tag=None):
    """

    :param consul_agent: A Consul object
    :type consul_agent: Consul
    :param service: The name of the consul servie
    :type service: str
    :param tag: A tag for the service
    :type tag: str|None

    :return: A dictionary of representation of the result of
    a query to /v1/health/service/<service>
    :rtype: dict

    """
    if tag:
        _, health_service = consul_agent.health.service(service, tag=tag)
    else:
        _, health_service = consul_agent.health.service(service)

    return health_service


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

    consul_agent = Consul(**consul_config.kwargs())
    sink = Sink(sink_config)

    dc = get_dc(consul_agent)
    log.debug('Running service availability check on '
              'Service:{service} Tag:{tag} DC:{dc}'.format(service=service,
                                                           tag=tag, dc=dc))

    consul_health_service = get_health_service(consul_agent, service, tag)
    ok, critical = get_node_status(consul_health_service)

    sink.ok_count(ok, service, dc, tag)
    sink.critical_count(critical, service, dc, tag)

    if ok + critical > 0:
        sink.ok_percent(float((ok / (ok + critical))), service, dc, tag)
        sink.critical_percent(float((critical / (ok + critical))),
                              service, dc, tag)

    return 0


def loop(liaison_config):
    """
    The main read loop.

    :param liaison_config: A LiasonConfig object
    :type liaison_config: LiaisonConfig
    """

    consul_config = liaison_config.consul_config
    sink_config = liaison_config.sink_config

    consul_agent = Consul(**consul_config.kwargs())

    services = get_services(consul_agent)
    check_service_jobs = create_check_service_jobs(services,
                                                   consul_config,
                                                   sink_config)

    pool, pool_size = create_pool(liaison_config)

    while len(check_service_jobs) > 0:
        if len(check_service_jobs) >= pool_size:
            pool.map(check_service, [check_service_jobs.pop()
                                     for _ in xrange(pool_size)])
        else:
            pool.map(check_service, [check_service_jobs.pop()
                                     for _ in xrange(len(check_service_jobs))])

        time.sleep(liaison_config.sleep)

    pool.close()
    pool.join()
