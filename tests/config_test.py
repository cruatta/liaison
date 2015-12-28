from __future__ import absolute_import

import sys
from liaison.config import LiaisonConfig, ConsulConfig, SinkConfig, load_config

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
