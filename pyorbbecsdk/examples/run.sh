#!/usr/bin/env bash
# Run a pyorbbecsdk example with the pip-bundled libOrbbecSDK first.
# Avoids: undefined symbol: ob_application_config_set_struct
# (ROS orbbec_camera's older libOrbbecSDK wins on LD_LIBRARY_PATH otherwise)
#
# Usage (from pyorbbecsdk repo root):
#   ./examples/run.sh examples/beginner/05_point_cloud.py
#   ./examples/run.sh examples/quick_start.py

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PKG_DIR="$(python - <<'PY'
import sys
from pathlib import Path
for p in sys.path:
    d = Path(p) / "pyorbbecsdk"
    if (d / "libOrbbecSDK.so.2").exists() or list(d.glob("pyorbbecsdk*.so")):
        print(d)
        break
else:
    sys.exit(1)
PY
)" || {
  echo "pyorbbecsdk not found for this python. Install with:"
  echo "  python -m pip install pyorbbecsdk2"
  exit 1
}

export LD_LIBRARY_PATH="${PKG_DIR}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <example.py> [args...]"
  echo "Example: $0 examples/beginner/05_point_cloud.py"
  exit 1
fi

exec python "$@"
