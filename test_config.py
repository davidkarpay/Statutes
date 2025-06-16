import unittest
import importlib.util
import os

class TestConfig(unittest.TestCase):
    def test_config_file_exists(self):
        self.assertTrue(os.path.exists('config.ini'))

    def test_config_values(self):
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        # Simulate reading as a flat file (no sections)
        with open('config.ini') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        keys = [line.split('=')[0].strip() for line in lines]
        self.assertIn('index_url', keys)
        self.assertIn('db_file', keys)
        self.assertIn('rate_limit_seconds', keys)
        self.assertIn('user_agent', keys)

if __name__ == '__main__':
    unittest.main()
