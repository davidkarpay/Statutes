import unittest
import logging
from unittest.mock import patch
import Statutes_at_5 as statutes

class TestScriptLogging(unittest.TestCase):
    def test_main_logs_info(self):
        with self.assertLogs('Statutes_at_5', level='INFO') as cm:
            with patch('Statutes_at_5.fetch_html', return_value=(None, None)):
                statutes.main()
        self.assertTrue(any('ERROR' in msg or 'INFO' in msg for msg in cm.output))

if __name__ == '__main__':
    unittest.main()
