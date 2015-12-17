from __future__ import absolute_import

import sys
from liaison.main import Liaison, get_node_status
from liaison.config import LiaisonConfig

if sys.version >= '3':
    import unittest
    import unittest.mock as mock
else:
    import unittest2 as unittest
    import mock


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

    def stub_create_check_service_jobs(self, services):
        check_service_jobs = list()
        for name, tags in services.items():
            for tag in tags:
                check_service_jobs.append(
                    {'service': name, 'tag': tag})
            check_service_jobs.append({'service': name, 'tag': None})
        return check_service_jobs

    #
    # 2015-12-16 - Cannot use autospec with static methods
    # https://bugs.python.org/issue23078
    # Leaving it off create_pool

    # FYI these can also be patched like this:
    # @mock.patch.object(liaison.consul.Consul, 'get_services', autospec=True)
    # @mock.patch.object(liaison.main.Liaison, 'create_pool')
    #
    @mock.patch('liaison.consul.Consul.get_services', autospec=True)
    @mock.patch('liaison.main.Liaison.create_pool')
    @mock.patch('liaison.main.Liaison.create_check_service_jobs',
                side_effect=stub_create_check_service_jobs, autospec=True)
    def test_loop_pool_size_small(self, mock_create_check_service_jobs,
                                  mock_create_pool, mock_get_services):

        mock_pool = mock.Mock()
        mock_pool_size = 1

        mock_get_services.return_value = {'srv1': ['a', 'b'],
                                          'srv2': ['c', 'd']}
        mock_create_pool.return_value = mock_pool, mock_pool_size

        liaison = Liaison(LiaisonConfig(sleep=0))
        liaison.loop()

        self.assertEqual(6, mock_pool.map.call_count)
        self.assertEqual(1, mock_create_check_service_jobs.call_count)

    @mock.patch('liaison.consul.Consul.get_services', autospec=True)
    @mock.patch('liaison.main.Liaison.create_pool')
    @mock.patch('liaison.main.Liaison.create_check_service_jobs',
                side_effect=stub_create_check_service_jobs, autospec=True)
    def test_loop_pool_size_big(self, mock_create_check_service_jobs,
                                mock_create_pool, mock_get_services):

        mock_pool = mock.Mock()
        mock_pool_size = 10

        mock_get_services.return_value = {'srv1': ['a', 'b'],
                                          'srv2': ['c', 'd']}
        mock_create_pool.return_value = mock_pool, mock_pool_size

        liaison = Liaison(LiaisonConfig(sleep=0))
        liaison.loop()

        self.assertEqual(1, mock_pool.map.call_count)
        self.assertEqual(1, mock_create_check_service_jobs.call_count)

