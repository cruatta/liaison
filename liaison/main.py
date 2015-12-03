from config import LiaisonConfig, ConsulConfig, StatsdConfig
import log

import consul
import statsd
import multiprocessing
import time

def check_service(check_service_job):
    """
    Check the availability of a consul service and send stats to StatsD.

    :param check_service_job: Dictionary containing job specification
    :type check_service_job: dict[str, str, ConsulConfig, StatsdConfig]

    :return Integer return code
    :rtype int
    """

    try:
        service = check_service_job['service']
        tag = check_service_job['tag']
        consul_config = check_service_job['consul_config']
        statsd_config = check_service_job['statsd_config']
    except KeyError as e:
        log.error(e.message)
        return 2

    nodes = dict()
    ok = 0
    failing = 0

    c = consul.Consul(**consul_config.kwargs())
    s = statsd.StatsClient(*statsd_config.args())

    try:
        dc = c.agent.self()['Config']['Datacenter']
    except Exception as e:
        log.error(e.message)
        return 2

    if tag:
        _, health_service = c.health.service(service, tag=tag)
    else:
        _, health_service = c.health.service(service)

    log.debug('Running service availability check on Service:{} Tag:{} DC:{}'.format(service, tag, dc))

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
            failing += 1
        else:
            ok += 1
    if tag:
        s.gauge('consul.{dc}.service.{srv}.{tag}.ok.count'.format(srv=service, tag=tag, dc=dc), ok)
        s.gauge('consul.{dc}.service.{srv}.{tag}.failing.count'.format(srv=service, tag=tag, dc=dc), failing)
        if ok + failing > 0:
            s.gauge('consul.{dc}.service.{srv}.{tag}.ok.percent'.format(srv=service, tag=tag, dc=dc),
                    float((ok / (ok + failing))))
            s.gauge('consul.{dc}.service.{srv}.{tag}.failing.percent'.format(srv=service, tag=tag, dc=dc),
                    float((failing / (ok + failing))))
    else:
        s.gauge('consul.{dc}.service.{srv}.ok.count'.format(srv=service, dc=dc), ok)
        s.gauge('consul.{dc}.service.{srv}.failing.count'.format(srv=service, dc=dc), failing)
        if ok + failing > 0:
            s.gauge('consul.{dc}.service.{srv}.ok.percent'.format(srv=service, dc=dc),
                    float((ok / (ok + failing))))
            s.gauge('consul.{dc}.service.{srv}.failing.percent'.format(srv=service, dc=dc),
                    float((failing / (ok + failing))))

    return 0


def loop(liaison_config, consul_config, statsd_config):
    """
    The main read loop.

    :param liaison_config: A LiasonConfig object
    :type liaison_config: LiaisonConfig

    :param consul_config: A ConsulConfig object
    :type consul_config: ConsulConfig

    :param statsd_config: A StatsdConfig object
    :type statsd_config: StatsdConfig
    """

    c = consul.Consul(**consul_config.kwargs())
    _, services = c.catalog.services()

    check_service_jobs = list()
    for name, tags in services.iteritems():
        for tag in tags:
            check_service_jobs.append({'service': name, 'tag': tag,
                                       'consul_config': consul_config, 'statsd_config': statsd_config})
        check_service_jobs.append({'service': name, 'tag': None,
                                   'consul_config': consul_config, 'statsd_config': statsd_config})

    pool_size = multiprocessing.cpu_count() if liaison_config.pool_size is None else liaison_config.pool_size
    p = multiprocessing.Pool(pool_size)

    while len(check_service_jobs) > 0:
        if len(check_service_jobs) >= pool_size:
            p.map(check_service, [check_service_jobs.pop() for _ in xrange(pool_size)])
        else:
            p.map(check_service, [check_service_jobs.pop() for _ in xrange(len(check_service_jobs))])
        time.sleep(liaison_config.pause_time)

    p.close()
    p.join()

if __name__ == "__main__":
    lc = LiaisonConfig()
    cc = ConsulConfig()
    sc = StatsdConfig()

    while True:
        loop(lc, cc, sc)
