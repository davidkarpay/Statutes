import unittest
from unittest.mock import patch
import sqlite3
from bs4 import BeautifulSoup
import Statutes_at_5 as statutes

class TestErrorHandling(unittest.TestCase):
    def test_network_error_handling(self):
        with patch('Statutes_at_5.requests.get', side_effect=statutes.requests.exceptions.RequestException):
            result = statutes.fetch_html('http://example.com')
            self.assertEqual(result, (None, None))

    def test_db_error_handling(self):
        html = '<table id="maintable"></table>'
        fake_soup = BeautifulSoup(html, 'html.parser')
        with patch('sqlite3.connect', side_effect=sqlite3.DatabaseError('DB error')), \
             patch('Statutes_at_5.fetch_html', return_value=(fake_soup, html.encode())):
            with self.assertRaises(sqlite3.DatabaseError):
                # Try to run main, which should raise the DB error
                statutes.main()

if __name__ == "__main__":
    unittest.main()
