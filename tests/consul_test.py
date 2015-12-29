from __future__ import absolute_import

import sys
from liaison import consul, config

if sys.version >= '3.3':
    import unittest
    import unittest.mock as mock
elif sys.version >= '3':
    import unittest
    import mock
else:
    import unittest2 as unittest
    import mock


class ConsulTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_dc(self):
        dc = 'test'
        cc = config.ConsulConfig(dc=dc)
        c = consul.Consul(cc)
        self.assertEquals(dc, c.api.dc)

