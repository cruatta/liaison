from config import LiaisonConfig, ConsulConfig, StatsdConfig

import consul
import statsd

import multiprocessing
import time

# Liaison - Send consul stats to statsd
# Simple Python implementation

def check_service(job):
    """

    :param job: Tuple that looks something like this ((service, tag), consul config, statsd config)
    :return:
    """

    print(job[0])
    service = job[0][0]
    tag = job[0][1]
    consul_config = job[1]
    statsd_config = job[2]

    nodes = dict()
    ok = 0
    failing = 0

    c = consul.Consul(**consul_config.kwargs())
    s = statsd.StatsClient(*statsd_config.args())

    if tag:
        _, health_service = c.health.service(service, tag=tag)
    else:
        _, health_service = c.health.service(service)

    dc = c.agent.self()['Config']['Datacenter']

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
    return


def loop(liaison_config, consul_config, statsd_config):
    """

    :param liaison_config:
    :param consul_config:
    :param statsd_config:
    :return:
    """

    pool_size = multiprocessing.cpu_count() if liaison_config.pool_size is None else liaison_config.pool_size

    x = list()
    c = consul.Consul(**consul_config.kwargs())
    _, services = c.catalog.services()

    for name, tags in services.iteritems():
        for tag in tags:
            x.append((name, tag))
        x.append((name, None))

    p = multiprocessing.Pool(pool_size)

    while len(x) > 0:
        if len(x) >= pool_size:
            p.map(check_service,
                  ((x.pop(), consul_config, statsd_config) for _ in xrange(pool_size)))
        else:
            p.map(check_service,
                  ((x.pop(), consul_config, statsd_config) for _ in xrange(len(x))))
        time.sleep(liaison_config.pause_time)

    p.close()
    p.join()

if __name__ == "__main__":
    liaison_config = LiaisonConfig()
    consul_config = ConsulConfig()
    statsd_config = StatsdConfig()

    while True:
        loop(liaison_config, consul_config, statsd_config)
