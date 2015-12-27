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
    @mock.patch('liaison.config.open')
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
    @mock.patch('liaison.config.open')
    def test_load_config_sink_options(self, mock_open, mock_load):
        mock_load.return_value = {
            'pool_size': 3,
            'sleep': 1,
            'consul': {},
            'sink': {
                'options': {
                    'host': '127.0.0.1'
                }
            }
        }

        lc = load_config('')

    @mock.patch('liaison.config.json.load')
    @mock.patch('liaison.config.open')
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
            lc = load_config('')
        except Exception as e:
            self.assertEqual(e.message, 'Invalid Sink configuration.')

