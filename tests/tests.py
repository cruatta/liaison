from liaison.sink import Sink, StatsdSink
from liaison.config import LiaisonConfig, ConsulConfig, SinkConfig, StatsdOptions

import sys
if sys.version_info.major > 2:
    import unittest
    from unittest import mock
else:
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    import mock

class SinkTests(unittest.TestCase):

    def setUp(self):
        self.sink = Sink(SinkConfig())
        self.sink.statsd = StatsdSink(StatsdOptions())
        self.sink.statsd.client.gauge = mock.MagicMock(return_value=None)

    def test_ok_count_no_tag(self):
        x = self.sink.ok_count(3, "service", "dc", None)
        assert x is None

    def test_ok_count_tag(self):
        x = self.sink.ok_count(3, "service", "dc", "tag")
        assert x is None
