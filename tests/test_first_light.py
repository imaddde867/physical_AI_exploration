"""Native-host checks of firmware code that has no hardware dependencies."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = ROOT / "firmware" / "first_light" / "core.h"


class FirstLightTest(unittest.TestCase):
    def test_pattern_and_canonical_command_subset(self):
        cc = shutil.which("cc") or shutil.which("clang")
        if not cc:
            self.skipTest("C compiler not available")
        program = r'''
#include <assert.h>
#include <stdint.h>
#include "core.h"
int main(void) {
    uint8_t line[BUDDY_ROW_BYTES];
    assert(BUDDY_WIDTH == 240 && BUDDY_HEIGHT == 280);
    assert(BUDDY_ROW_OFFSET == 20 && sizeof(line) == 480);
    buddy_pattern_row(0, line);
    assert(line[0] == 0xFF && line[1] == 0xFF);
    buddy_pattern_row(279, line);
    assert(line[0] == 0 && line[479] == 0);
    buddy_pattern_row(140, line);
    const uint16_t bars[8] = {0xF800,0x07E0,0x001F,0xFFE0,0xF81F,0x07FF,0xFFFF,0};
    for (unsigned i = 0; i < 8; ++i) {
        unsigned x = i * 30 + 15;
        uint16_t actual = (uint16_t)(line[x*2] << 8 | line[x*2+1]);
        assert(actual == bars[i]);
    }
    assert(buddy_parse("{\"v\":1,\"t\":\"ping\"}") == BUDDY_PING);
    assert(buddy_parse("{\"v\":1,\"t\":\"sleep\"}") == BUDDY_SLEEP);
    assert(buddy_parse("{\"v\":1,\"t\":\"wake\"}") == BUDDY_WAKE);
    assert(buddy_parse("{\"v\":1,\"t\":\"face\"}") == BUDDY_UNSUPPORTED);
    assert(buddy_parse("{\"v\":2,\"t\":\"ping\"}") == BUDDY_UNSUPPORTED);
    assert(buddy_parse("{\"t\":\"ping\",\"v\":1}") == BUDDY_UNSUPPORTED);
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "check.c"
            out = Path(tmp) / "check"
            src.write_text(program)
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(HEADER.parent),
                            str(src), "-o", str(out)], check=True, capture_output=True, text=True)
            subprocess.run([str(out)], check=True, capture_output=True, text=True)

    def test_host_encoder_uses_supported_first_light_messages(self):
        from daemon.protocol import encode
        for cmd in ("ping", "sleep", "wake"):
            self.assertEqual(encode({"v": 1, "t": cmd}),
                             ('{"v":1,"t":"' + cmd + '"}\n').encode())


if __name__ == "__main__":
    unittest.main()
