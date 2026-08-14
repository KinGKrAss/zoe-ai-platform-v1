import unittest

from zoe_memory.memory_core import MemoryCore


class MemoryCorePureTests(unittest.TestCase):
    def test_dedupe_key_is_deterministic_and_normalized(self) -> None:
        first = MemoryCore.dedupe_key("  Zoë remembers this fact. ")
        second = MemoryCore.dedupe_key("zoë   remembers this fact.")
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_dedupe_key_changes_with_content(self) -> None:
        self.assertNotEqual(
            MemoryCore.dedupe_key("first fact"),
            MemoryCore.dedupe_key("second fact"),
        )


if __name__ == "__main__":
    unittest.main()
