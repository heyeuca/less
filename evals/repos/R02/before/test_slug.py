import unittest

import slug


class SlugTest(unittest.TestCase):
    def setUp(self):
        slug._reset_cache()

    def test_slugify(self):
        self.assertEqual(slug.slugify("Hello, World!"), "hello-world")

    def test_cache_holds_one_entry(self):
        slug.slugify("A B")
        self.assertEqual(len(slug._CACHE), 1)


if __name__ == "__main__":
    unittest.main()
