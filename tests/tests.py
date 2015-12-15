from liaison.sink import Sink, StatsdSink, SinkException
from liaison.config import \
    SinkConfig, StatsdOptions

import sys
if sys.version_info.major > 2:
    import unittest
else:
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest


class StatsdSinkTests(unittest.TestCase):

    def setUp(self):
        self.base = Sink(SinkConfig())
        self.base.sink = StatsdSink(StatsdOptions())
        self.base.sink.client.gauge = lambda x, y, d=None: (x, y, d)

    def test_ok_count_no_tag(self):
        x = self.base.ok_count(3, "srv1", "dc1", None)
        self.assertTrue(x == (
            'consul.service.dc1.srv1.ok.count', 3, None))

    def test_ok_count_tag(self):
        x = self.base.ok_count(3, "srv1", "dc1", "tag")
        self.assertTrue(x == (
            'consul.service.dc1.srv1.tag.ok.count', 3, None))

    def test_ok_percent_no_tag(self):
        x = self.base.ok_percent(0.9, "srv1", "dc1", None)
        self.assertTrue(x == (
            'consul.service.dc1.srv1.ok.percent', 0.9, None))

    def test_ok_percent_tag(self):
        x = self.base.ok_percent(0.9, "srv1", "dc1", "tag")
        self.assertTrue(x == (
            'consul.service.dc1.srv1.tag.ok.percent', 0.9, None))

    def test_critical_percent_no_tag(self):
        x = self.base.critical_percent(0.9, "srv1", "dc1", None)
        self.assertTrue(x == (
            'consul.service.dc1.srv1.critical.percent', 0.9, None))

    def test_critical_percent_tag(self):
        x = self.base.critical_percent(0.9, "srv1", "dc1", "tag")
        self.assertTrue(x == (
            'consul.service.dc1.srv1.tag.critical.percent', 0.9, None))

    def test_critical_count_no_tag(self):
        x = self.base.critical_count(3, "srv1", "dc1", None)
        self.assertTrue(x == (
            'consul.service.dc1.srv1.critical.count', 3, None))

    def test_critical_count_tag(self):
        x = self.base.critical_count(3, "srv1", "dc1", "tag")
        self.assertTrue(x == (
            'consul.service.dc1.srv1.tag.critical.count', 3, None))

    def test_invalid_sink(self):
        with self.assertRaises(SinkException):
            config = SinkConfig(type="statsd")
            config.type = "invalid"
            Sink(config)
