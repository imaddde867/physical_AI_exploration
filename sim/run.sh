#!/bin/bash
# Launch the live simulator with a Tk runtime that actually renders on macOS.
# System Python 3.9's bundled Tk 8.6.8 opens windows that paint blank on macOS 26;
# the uv Python's Tcl/Tk does render, but needs TCL_LIBRARY/TK_LIBRARY pointed at it.
uv_lib="$(ls -d "$HOME/.local/share/uv/python/"cpython-3.12*/ 2>/dev/null | head -1)"
export TCL_LIBRARY="$uv_lib/lib/tcl8.6" TK_LIBRARY="$uv_lib/lib/tk8.6"
exec "$HOME/.local/bin/python3.12" -m sim.runner "$@"
