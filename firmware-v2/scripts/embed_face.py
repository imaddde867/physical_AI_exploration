Import("env")
from pathlib import Path
import sys
project = Path(env.subst("$PROJECT_DIR")).resolve()
sys.path.insert(0, str(project.parent))
from tools.amoled_face import generate
# Do not rewrite checked-in assets during compilation.
generate(project / ".pio" / "preview", project / "include" / "face_frames.h")
