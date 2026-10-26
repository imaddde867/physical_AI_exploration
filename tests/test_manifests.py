import copy
import tempfile
import unittest
from pathlib import Path

from tools.check_repository import (ROOT, read_json, check_bom, check_options,
                                    check_markdown_links, check_svgs, check_firmware_contract)


class ManifestTests(unittest.TestCase):
    def test_bom_recalculates(self):
        check_bom(read_json(ROOT / "hardware/bom.json"))

    def test_wrong_total_is_rejected(self):
        data = copy.deepcopy(read_json(ROOT / "hardware/bom.json"))
        data["expected_total"] = "40.00"
        with self.assertRaises(AssertionError):
            check_bom(data)

    def test_option_ids_and_compatibility(self):
        check_options(read_json(ROOT / "hardware/options.json"))

    def test_local_links_and_svgs(self):
        self.assertEqual([], check_markdown_links(ROOT))
        self.assertEqual([], check_svgs(ROOT))

    def test_broken_html_image_link_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                '<p align="center"><img src="assets/missing.png"></p>',
                encoding="utf-8",
            )
            self.assertEqual(
                ["README.md -> assets/missing.png"],
                check_markdown_links(root),
            )

    def test_firmware_assumptions(self):
        check_firmware_contract(ROOT)


if __name__ == "__main__":
    unittest.main()
