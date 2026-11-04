import unittest
from datetime import date

from dates import parse_date


class ParseTest(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date("2026-11-04"), date(2026, 11, 4))


if __name__ == "__main__":
    unittest.main()
