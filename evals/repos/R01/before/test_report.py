import unittest

from report import render


class RenderTest(unittest.TestCase):
    def test_compact(self):
        self.assertEqual(render([("a", 1)], compact=True), "a: 1")

    def test_aligned(self):
        self.assertEqual(render([("a", 1)]), "a".ljust(12) + "1".rjust(8))


if __name__ == "__main__":
    unittest.main()
