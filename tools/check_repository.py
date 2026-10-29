"""Offline validation of the hardware catalog, BOM math and repository links.

Usage (from repo root):
    python3 tools/check_repository.py

No network calls, hardware access, external packages or vendor checkout.
"""
from __future__ import annotations

import json
import re
import sys
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
URL_SCHEMES = ("https:", "http:", "mailto:", "tel:", "data:")
MD_LINKS = re.compile(r"\[[^\]]*\]\(([^)\n]+)\)")
HTML_IMAGES = re.compile(r"""<img\b[^>]*\bsrc=["']([^"']+)["']""", re.IGNORECASE)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def check_bom(data: dict) -> None:
    assert data["currency"] == "EUR"
    assert data["schema_version"] == 1
    ids = [item["id"] for item in data["items"]]
    assert len(ids) == len(set(ids)), "Duplicate BOM line ID"
    assert "display_gc9a01" in ids
    assert "esp32_s3_n16r8" in ids
    total = sum(
        (Decimal(item["unit_price"]) * int(item["quantity"])
         for item in data["items"]),
        Decimal("0"),
    )
    assert total == Decimal(data["expected_total"]), (
        f"BOM total mismatch: {total} != {data['expected_total']}"
    )
    omitted = sum(
        (Decimal(item["unit_price"]) * int(item["quantity"])
         for item in data["items"] if item.get("optional_if_already_owned")),
        Decimal("0"),
    )
    assert total - omitted == Decimal(data["expected_total_without_cable"])
    for item in data["items"]:
        assert int(item["quantity"]) > 0, item["id"]
        assert Decimal(item["unit_price"]) >= 0, item["id"]
        assert item["url"].startswith("https://"), item["id"]
        assert item["verify"].strip(), item["id"]


def check_options(data: dict) -> None:
    assert data["schema_version"] == 1
    options = data["options"]
    assert len(options) >= 7, "Catalog is missing the intended alternatives"
    ids = [item["id"] for item in options]
    assert len(ids) == len(set(ids)), "Duplicate option ID"
    assert data["selected_track"] in ids
    assert data.get("implemented_track") in ids, "Missing or unknown implemented track"
    for item in options:
        assert item["source_url"].startswith("https://")
        assert int(Decimal(item["price"]["amount"])) >= 0
        assert item["price"]["covers"].strip()
        assert item["recommendation"].strip()
        assert all(isinstance(x, int) and 1 <= x <= 9 for x in item["related_reels"])
    taby = next(q for q in options if q["id"] == "taby-round-amoled")
    assert "1.32" in taby["name"]
    assert "not compatible" in taby["software"].lower()
    implemented = next(q for q in options if q["id"] == data["implemented_track"])
    assert "GC9A01" in implemented["hardware"], "Firmware currently implements GC9A01 only"
    assert implemented["price"]["currency"] == "EUR"


def check_markdown_links(root: Path) -> list[str]:
    broken = []
    for path in sorted(root.rglob("*.md")):
        # Exclude hidden transient checkout/cache locations if run locally.
        if ".git" in path.parts or ".venv" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        destinations = [m.group(1) for m in MD_LINKS.finditer(text)]
        destinations.extend(m.group(1) for m in HTML_IMAGES.finditer(text))
        for raw_destination in destinations:
            destination = raw_destination.strip().split(" ", 1)[0].strip("<>")
            if not destination or destination.startswith(URL_SCHEMES + ("#",)):
                continue
            destination = unquote(destination.split("#", 1)[0].split("?", 1)[0])
            if not destination:
                continue
            if destination.startswith("/"):
                target = root / destination.lstrip("/")
            else:
                target = path.parent / destination
            if not target.resolve().is_relative_to(root.resolve()) or not target.exists():
                broken.append(f"{path.relative_to(root)} -> {raw_destination}")
    return broken


def check_svgs(root: Path) -> list[str]:
    invalid = []
    for svg in sorted((root / "assets").glob("*.svg")):
        try:
            parsed = ElementTree.parse(svg)
            if not parsed.getroot().tag.endswith("svg"):
                invalid.append(f"{svg.name}: root element is not SVG")
        except ElementTree.ParseError as exc:
            invalid.append(f"{svg.name}: {exc}")
    return invalid


def check_firmware_contract(root: Path) -> None:
    code = (root / "firmware/src/main.cpp").read_text(encoding="utf-8")
    board = (root / "firmware/platformio.ini").read_text(encoding="utf-8")
    assert "Adafruit_GC9A01A.h" in code
    assert "GC9A01A @ 1.2.0" in board
    for pin in ("TFT_MOSI = 11", "TFT_SCLK = 12", "TFT_CS = 10",
                "TFT_DC = 13", "TFT_RST = 14", "IMU_SDA = 8", "IMU_SCL = 9"):
        assert pin in code, f"Firmware pin mapping changed: {pin}"
    assert "init_sent_unverified" in code, "SPI display cannot self-report illumination"
    assert "SSD1306" not in code + board, "Old OLED code returned"


def main() -> int:
    try:
        bom = read_json(ROOT / "hardware/bom.json")
        options = read_json(ROOT / "hardware/options.json")
        check_bom(bom)
        check_options(options)
        check_firmware_contract(ROOT)
        missing = check_markdown_links(ROOT)
        svg_errors = check_svgs(ROOT)
        if missing or svg_errors:
            for error in missing + svg_errors:
                print("ERROR:", error, file=sys.stderr)
            return 1
    except (AssertionError, KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: BOM €{bom['expected_total']}, {len(options['options'])} hardware choices, Markdown/HTML image links, SVG and firmware contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
