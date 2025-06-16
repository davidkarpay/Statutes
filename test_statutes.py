import unittest
from unittest.mock import patch, MagicMock
import Statutes_at_5 as statutes
import requests

class TestStatutesScraper(unittest.TestCase):
    def test_fetch_html_success(self):
        with patch('Statutes_at_5.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'<html></html>'
            mock_get.return_value = mock_response
            soup, content = statutes.fetch_html('http://example.com')
            self.assertIsNotNone(soup)
            self.assertEqual(content, b'<html></html>')

    def test_fetch_html_failure(self):
        with patch('Statutes_at_5.requests.get', side_effect=requests.exceptions.RequestException('Network error')):
            soup, content = statutes.fetch_html('http://example.com', retries=1)
            self.assertIsNone(soup)
            self.assertIsNone(content)

    def test_get_title_links(self):
        html = '''<table id="maintable"><a href="index.cfm?App_mode=Display_Index&Title_Request=TITLE I">TITLE I</a></table>'''
        soup = statutes.BeautifulSoup(html, 'html.parser')
        links = statutes.get_title_links(soup, ["TITLE I"])
        self.assertEqual(len(links), 1)
        self.assertIn('TITLE I', links[0]['text'])

    def test_get_chapter_links(self):
        html = '''<a href="App_mode=Display_Statute&ContentsIndex.html&StatuteYear=2025">Chapter 1</a>'''
        soup = statutes.BeautifulSoup(html, 'html.parser')
        links = statutes.get_chapter_links(soup)
        self.assertEqual(len(links), 1)
        self.assertIn('Chapter 1', links[0]['text'])

    def test_get_statute_links(self):
        html = '''<a href="index.cfm?App_mode=Display_Statute&Sections/0001.01.html">1.01</a>'''
        soup = statutes.BeautifulSoup(html, 'html.parser')
        links = statutes.get_statute_links(soup)
        self.assertEqual(len(links), 1)
        self.assertIn('1.01', links[0]['text'])

    def test_extract_statute_data(self):
        html = '''<h2>1.01 Statute Title</h2><table id="maintable"><p>(1) Subsection text.</p></table>'''
        soup = statutes.BeautifulSoup(html, 'html.parser')
        data = statutes.extract_statute_data(soup, 'http://example.com')
        self.assertEqual(data['number'], '1.01')
        self.assertEqual(data['title'], '1.01 Statute Title')
        self.assertEqual(len(data['subsections']), 1)

    def test_scan_references(self):
        text = "See s. 1.01 and chapter 2."
        refs = statutes.scan_references(text)
        self.assertTrue(any(ref['type'] == 'section' for ref in refs))
        self.assertTrue(any(ref['type'] == 'chapter' for ref in refs))

if __name__ == '__main__':
    unittest.main()
