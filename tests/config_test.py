from __future__ import absolute_import

import sys
from liaison.config import LiaisonConfig, \
    ConsulConfig, SinkConfig, StatsdOptions,\
    load_config

if sys.version >= '3.3':
    import unittest
    import unittest.mock as mock
elif sys.version >= '3':
    import unittest
    import mock
else:
    import unittest2 as unittest
    import mock


class ConfigTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_liaison_config(self):
        cc = ConsulConfig()
        sc = SinkConfig()
        l = LiaisonConfig()
        self.assertEqual(l.consul_config.kwargs(), cc.kwargs())
        self.assertEqual(l.sink_config.type, sc.type)
        self.assertEqual(l.sink_config.opts.args(), sc.opts.args())

    def test_invalid_consul_config_liaison_config(self):
        try:
            LiaisonConfig(consul_config=99)
        except Exception as e:
            self.assertEqual(
                str(e),
                "LiaisonConfig | Bad consul_config parameter. Invalid type")

    def test_invalid_sink_config_liaison_config(self):
        try:
            LiaisonConfig(sink_config=99)
        except Exception as e:
            self.assertEqual(
                str(e),
                "LiaisonConfig | Bad sink_config parameter. Invalid type")

    def test_valid_consul_config_liaison_config(self):
        host = '192.168.0.1'
        cc = ConsulConfig(host=host)
        l = LiaisonConfig(consul_config=cc)
        self.assertEqual(l.consul_config.host, host)

    def test_valid_sink_config_liaison_config(self):
        host = '192.168.0.1'
        port = '9999'
        sc = SinkConfig(options={'host': host, 'port': port})
        l = LiaisonConfig(sink_config=sc)
        self.assertEqual(l.sink_config.opts.args(), [host, port])

    @mock.patch('liaison.config.json.load')
    @mock.patch('liaison.config.open', create=True)
    def test_load_config(self, mock_open, mock_load):
        mock_load.return_value = {
            'pool_size': 3,
            'sleep': 1,
            'consul': {},
            'sink': {}
        }
        lc = load_config('/tmp/file')
        mock_open.assert_called_with('/tmp/file')
        self.assertEqual(lc.pool_size, 3)
        self.assertEqual(lc.sleep, 1)
        self.assertIsInstance(lc, LiaisonConfig)
        self.assertIsInstance(lc.consul_config, ConsulConfig)
        self.assertIsInstance(lc.sink_config, SinkConfig)

    @mock.patch('liaison.config.json.load')
    @mock.patch('liaison.config.open', create=True)
    def test_load_config_with_options(self, mock_open, mock_load):
        mock_load.return_value = {
            'pool_size': 3,
            'sleep': 1,
            'consul': {
                'consistency': 'stale',
                'dc': 'dc99'
            },
            'sink': {
                'options': {
                    'host': '192.168.0.1',
                    'port': 8135
                }
            }
        }

        lc = load_config('')
        self.assertEqual(lc.sink_config.opts.args(), ['192.168.0.1', 8135])
        self.assertEqual(lc.consul_config.kwargs(), {
            'host': '127.0.0.1',
            'port': 8500,
            'token': None,
            'scheme': 'http',
            'consistency': 'stale',
            'dc': 'dc99',
            'verify': True
        })

    @mock.patch('liaison.config.json.load')
    @mock.patch('liaison.config.open', create=True)
    def test_load_config_bad_sink_options(self, mock_open, mock_load):
        mock_load.return_value = {
            'pool_size': 3,
            'sleep': 1,
            'consul': {},
            'sink': {
                'type': 'bad',
                'options': {}
            }
        }
        try:
            load_config('')
        except Exception as e:
            self.assertEqual(str(e), 'Invalid Sink configuration.')
