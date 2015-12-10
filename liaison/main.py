import log
from sink import Sink

import consul
import multiprocessing
import time


def check_service(check_service_job):
    """
    Check the availability of a consul service and send stats to StatsD.

    :param check_service_job: Dictionary containing job specification
    :type check_service_job: dict[str, str, ConsulConfig, StatsdConfig]

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

    nodes = dict()
    ok = 0
    critical = 0

    c = consul.Consul(**consul_config.kwargs())
    s = Sink(sink_config)

    try:
        dc = c.agent.self()['Config']['Datacenter']
    except KeyError as e:
        log.error("Missing key {e} in Agent self and cannot "
                  "get DC".format(e=e))
        return 2

    log.debug('Running service availability check on '
              'Service:{service} Tag:{tag} DC:{dc}'.format(service=service,
                                                           tag=tag, dc=dc))

    if tag:
        _, health_service = c.health.service(service, tag=tag)
    else:
        _, health_service = c.health.service(service)

    for node in health_service:
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

    s.ok_count(ok, service, dc, tag)
    s.critical_count(critical, service, dc, tag)

    if ok + critical > 0:
        s.ok_percent(float((ok / (ok + critical))), service, dc, tag)
        s.critical_percent(float((critical / (ok + critical))),
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

    c = consul.Consul(**consul_config.kwargs())
    index, services = c.catalog.services()

    check_service_jobs = list()
    for name, tags in services.iteritems():
        for tag in tags:
            check_service_jobs.append({'service': name, 'tag': tag,
                                       'consul_config': consul_config,
                                       'sink_config': sink_config})
        check_service_jobs.append({'service': name, 'tag': None,
                                   'consul_config': consul_config,
                                   'sink_config': sink_config})

    if liaison_config.pool_size is None:
        pool_size = multiprocessing.cpu_count()
    else:
        pool_size = liaison_config.pool_size

    p = multiprocessing.Pool(pool_size)

    while len(check_service_jobs) > 0:
        if len(check_service_jobs) >= pool_size:
            p.map(check_service, [check_service_jobs.pop()
                                  for _ in xrange(pool_size)])
        else:
            p.map(check_service, [check_service_jobs.pop()
                                  for _ in xrange(len(check_service_jobs))])
        time.sleep(liaison_config.sleep)

    p.close()
    p.join()
