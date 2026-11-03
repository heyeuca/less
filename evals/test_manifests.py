"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import json
import unittest

import run

MANIFESTS = (".claude-plugin", ".cursor-plugin")


def load(directory, name):
    return json.loads((run.ROOT / directory / name).read_text())


class ManifestTest(unittest.TestCase):
    def test_plugin_manifests_agree(self):
        # A release bumps every manifest; a missed one ships a stale version.
        claude, cursor = (load(d, "plugin.json") for d in MANIFESTS)
        for key in ("name", "version", "description", "license", "repository"):
            with self.subTest(key=key):
                self.assertEqual(claude[key], cursor[key])

    def test_marketplaces_list_the_same_plugin(self):
        claude, cursor = (load(d, "marketplace.json")["plugins"] for d in MANIFESTS)
        self.assertEqual(claude, cursor)


if __name__ == '__main__':
    unittest.main()
