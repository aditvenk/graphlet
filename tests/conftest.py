import sys
from pathlib import Path


# Ensure the project root is importable when tests run without installing the
# package. Pytest may set the CWD to the tests directory when using "testpaths".
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
