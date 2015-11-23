import consul
import time
import statsd

# Liaison - Send consul stats to statsd
# Simple Python implementation


def gauge_service_health(srv_tag):
    """

    :param srv_tag:
    :return:
    """

    nodes = dict()
    ok = 0
    failing = 0

    c = consul.Consul()
    s = statsd.StatsClient('localhost', 8125)
    dc = c.agent.self()['Config']['Datacenter']

    srv = srv_tag[0]
    tag = srv_tag[1]

    if tag:
        _, health_service = c.health.service(srv, tag=tag)

    else:
        _, health_service = c.health.service(srv)

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
        s.gauge('consul.{dc}.service.{srv}.{tag}.ok.count'.format(srv=srv, tag=tag, dc=dc), ok)
        s.gauge('consul.{dc}.service.{srv}.{tag}.failing.count'.format(srv=srv, tag=tag, dc=dc), failing)
        if ok + failing > 0:
            s.gauge('consul.{dc}.service.{srv}.{tag}.ok.percent'.format(srv=srv, tag=tag, dc=dc),
                    float((ok / (ok + failing))))
            s.gauge('consul.{dc}.service.{srv}.{tag}.failing.percent'.format(srv=srv, tag=tag, dc=dc),
                    float((failing / (ok + failing))))
    else:
        s.gauge('consul.{dc}.service.{srv}.ok.count'.format(srv=srv, dc=dc), ok)
        s.gauge('consul.{dc}.service.{srv}.failing.count'.format(srv=srv, dc=dc), failing)
        if ok + failing > 0:
            s.gauge('consul.{dc}.service.{srv}.ok.percent'.format(srv=srv, dc=dc),
                    float((ok / (ok + failing))))
            s.gauge('consul.{dc}.service.{srv}.failing.percent'.format(srv=srv, dc=dc),
                    float((failing / (ok + failing))))


def loop(pool_size=10, pause=30):
    """

    :param pool_size:
    :param pause:
    :return:
    """

    x = list()
    c = consul.Consul()
    _, srv = c.catalog.services()

    for name, tags in srv.iteritems():
        for tag in tags:
            x.append((name, tag))
        x.append((name, None))

    while len(x) > 0:
        gauge_service_health(x.pop())
        time.sleep(pause)


if __name__ == "__main__":
    while True:
        loop()
