from liaison.main import create_pool, create_check_service_jobs, \
    get_node_status, get_dc, get_health_service, get_services, \
    loop

from liaison.config import LiaisonConfig

import sys
if sys.version >= '3':
    import unittest
else:
    import unittest2 as unittest


class MainTests(unittest.TestCase):

    def test_loop(self):
        lc = LiaisonConfig()
        loop(lc)
