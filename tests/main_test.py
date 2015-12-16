from __future__ import absolute_import

import sys
from liaison.main import Liaison
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
