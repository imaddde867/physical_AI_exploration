# PlatformIO pre-build hook. Requires only the Python standard library.
# Run from either the USB/OTG or CH343P UART build environment.
Import("env")
from pathlib import Path
import sys

project = Path(env.subst("$PROJECT_DIR")).resolve()
sys.path.insert(0, str(project.parent))
from tools.face_asset import generate

meta = generate(project.parent / "assets" / "face-idle-240.png",
                project / "include" / "face_asset.h")
print(f"Approved single-face asset: {meta['rle_bytes']} RLE bytes; SHA256 {meta['sha256'][:12]}")
