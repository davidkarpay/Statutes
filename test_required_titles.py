import unittest
import Statutes_at_5 as statutes

class TestRequiredTitles(unittest.TestCase):
    def test_all_titles_present(self):
        expected_titles = [
            "TITLE I", "TITLE II", "TITLE III", "TITLE IV", "TITLE V", "TITLE VI",
            "TITLE VII", "TITLE VIII", "TITLE IX", "TITLE X", "TITLE XI", "TITLE XII", "TITLE XIII", "TITLE XIV", "TITLE XV", "TITLE XVI", "TITLE XVII", "TITLE XVIII", "TITLE XIX", "TITLE XX", "TITLE XXI", "TITLE XXII", "TITLE XXIII", "TITLE XXIV", "TITLE XXV", "TITLE XXVI", "TITLE XXVII", "TITLE XXVIII", "TITLE XXIX", "TITLE XXX", "TITLE XXXI", "TITLE XXXII", "TITLE XXXIII", "TITLE XXXIV", "TITLE XXXV", "TITLE XXXVI", "TITLE XXXVII", "TITLE XXXVIII", "TITLE XXXIX", "TITLE XL", "TITLE XLI", "TITLE XLII", "TITLE XLIII", "TITLE XLIV", "TITLE XLV", "TITLE XLVI", "TITLE XLVII", "TITLE XLVIII", "TITLE XLIX"
        ]
        for title in expected_titles:
            self.assertIn(title, statutes.required_titles)

if __name__ == "__main__":
    unittest.main()
