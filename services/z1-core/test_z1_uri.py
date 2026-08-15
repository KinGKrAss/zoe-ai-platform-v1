import unittest

from z1_uri import Z1URIError, parse_z1_uri, resolve_z1_reference


class Z1URITests(unittest.TestCase):
    def test_examples(self):
        examples = [
            "z1://3d/assets/GAIA-000123/model.drc",
            "z1://ppt/token/PPT",
            "z1://finance/accounts/main",
            "z1://memory/zoe/entries/123",
            "z1://documents/contracts/2026/001",
            "z1://agents/zoe/GOD-001",
        ]
        for value in examples:
            parsed = parse_z1_uri(value)
            self.assertEqual(parsed.uri, value)

    def test_dot_segment_removal(self):
        parsed = parse_z1_uri("z1://documents/contracts/2026/../2025/./001")
        self.assertEqual(parsed.uri, "z1://documents/contracts/2025/001")

    def test_relative_resolution(self):
        base = "z1://documents/contracts/2026/001/"
        self.assertEqual(
            resolve_z1_reference("../2025/002", base).uri,
            "z1://documents/contracts/2026/2025/002",
        )

    def test_invalid_scheme(self):
        with self.assertRaises(Z1URIError):
            parse_z1_uri("https://example.com/resource")

    def test_missing_namespace(self):
        with self.assertRaises(Z1URIError):
            parse_z1_uri("z1:///resource")

    def test_userinfo_rejected(self):
        with self.assertRaises(Z1URIError):
            parse_z1_uri("z1://user@example/resource")


if __name__ == "__main__":
    unittest.main()
