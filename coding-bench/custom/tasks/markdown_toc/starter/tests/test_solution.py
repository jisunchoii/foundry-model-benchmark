import unittest

from solution import build_toc


class TocTests(unittest.TestCase):
    def test_level_two_and_three_only(self):
        md = "# Title\n\n## Install Now!\ntext\n### Windows Setup\n#### Skip\n## API Reference"
        self.assertEqual(
            build_toc(md),
            "- [Install Now!](#install-now)\n  - [Windows Setup](#windows-setup)\n- [API Reference](#api-reference)",
        )

    def test_duplicate_headings_get_suffix(self):
        md = "## Usage\n## Usage\n### Usage"
        self.assertEqual(build_toc(md), "- [Usage](#usage)\n- [Usage](#usage-1)\n  - [Usage](#usage-2)")


if __name__ == "__main__":
    unittest.main()
