from __future__ import absolute_import

import sys
from liaison.main import Liaison, get_node_status
from liaison.config import LiaisonConfig
if sys.version >= '3':
    import unittest
else:
    import unittest2 as unittest


class MainTests(unittest.TestCase):
    def setUp(self):
        self.liaison = Liaison(LiaisonConfig())

    def test_create_pool(self):
        import multiprocessing.pool

        l = LiaisonConfig()
        pool, _ = self.liaison.create_pool(l)
        self.assertTrue(isinstance(pool, multiprocessing.pool.Pool))

    def test_create_pool_size_none(self):
        from multiprocessing import cpu_count

        l = LiaisonConfig()
        l.pool_size = None
        _, pool_size = self.liaison.create_pool(l)
        self.assertTrue(pool_size == cpu_count())

    def test_create_pool_size(self):
        l = LiaisonConfig()
        l.pool_size = 10
        _, pool_size = self.liaison.create_pool(l)
        self.assertTrue(pool_size == 10)

    def test_create_service_jobs(self):
        from liaison.config import ConsulConfig, SinkConfig
        services = dict()
        services['srv1'] = [None, 'tag1']
        services['srv2'] = [None]
        services['srv3'] = ['tag1', 'tag2']
        jobs = self.liaison.create_check_service_jobs(services)
        for job in jobs:
            self.assertTrue('service' in job)
            self.assertTrue(isinstance(job['service'], str))
            self.assertTrue('tag' in job)
            self.assertTrue(isinstance(job['tag'], str) or job['tag'] is None)
            self.assertTrue('consul_config' in job)
            self.assertTrue(isinstance(job['consul_config'], ConsulConfig))
            self.assertTrue('sink_config' in job)
            self.assertTrue(isinstance(job['sink_config'], SinkConfig))

    def test_get_node_status(self):
        nodes = list()
        node_a = {
            'Node': {
                'Node': 'node_c'
            },
            'Checks': []
        }
        node_b = {
            'Node': {
                'Node': 'node_b'
            },
            'Checks': [
                {
                    'Status': 'passing'
                },
                {
                    'Status': 'passing'
                },
                {
                    'Status': 'warning'
                },
                {
                    'Status': 'bogus'
                }
            ]
        }
        node_c = {
            'Node': {
                'Node': 'node_a'
            },
            'Checks': [
                {
                    'Status': 'passing'
                },
                {
                    'Status': 'critical'
                },
                {
                    'Status': 'warning'
                },
                {
                    'Status': 'bogus'
                }
            ]
        }
        nodes.append(node_a)
        self.assertEqual(get_node_status(nodes), (1, 0))
        nodes.append(node_b)
        self.assertEqual(get_node_status(nodes), (2, 0))
        nodes.append(node_c)
        self.assertEqual(get_node_status(nodes), (2, 1))
