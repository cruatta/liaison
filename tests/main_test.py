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
        try:
            from types import NoneType
        except ImportError:
            NoneType = type(None)
        from types import StringType
        from liaison.config import ConsulConfig, SinkConfig
        services = dict()
        services['srv1'] = [None, 'tag1']
        services['srv2'] = [None]
        services['srv3'] = ['tag1', 'tag2']
        jobs = self.liaison.create_check_service_jobs(services)
        for job in jobs:
            self.assertTrue('service' in job)
            self.assertTrue(type(job['service']) is StringType)
            self.assertTrue('tag' in job)
            self.assertTrue(type(job['tag']) is StringType or NoneType)
            self.assertTrue('consul_config' in job)
            self.assertTrue(type(job['consul_config']) is ConsulConfig)
            self.assertTrue('sink_config' in job)
            self.assertTrue(type(job['sink_config']) is SinkConfig)
