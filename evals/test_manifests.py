"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(directory):
    return json.loads((ROOT / directory / "plugin.json").read_text(encoding="utf-8"))


class ManifestTest(unittest.TestCase):
    def test_plugin_manifests_agree(self):
        # A release bumps every manifest; a missed one ships a stale version.
        claude, cursor = load(".claude-plugin"), load(".cursor-plugin")
        for key in ("name", "version", "description", "license", "repository"):
            with self.subTest(key=key):
                self.assertEqual(claude[key], cursor[key])


if __name__ == '__main__':
    unittest.main()
