import unittest

import logging
from unittest.mock import patch

class TestLogging(unittest.TestCase):
    def test_logging_info(self):
        logger = logging.getLogger('test_logger')
        with self.assertLogs(logger, level='INFO') as cm:
            logger.info('This is an info message')
        self.assertIn('INFO:test_logger:This is an info message', cm.output)

    def test_logging_error(self):
        logger = logging.getLogger('test_logger')
        with self.assertLogs(logger, level='ERROR') as cm:
            logger.error('This is an error message')
        self.assertIn('ERROR:test_logger:This is an error message', cm.output)

if __name__ == '__main__':
    unittest.main()
