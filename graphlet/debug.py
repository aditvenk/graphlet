import os, sys

_ENABLE = os.environ.get("GRAPHLET_DEBUG", "").strip()

def enabled() -> bool:
    return bool(_ENABLE)

def log(*args, **kwargs):
    if enabled():
        print("[graphlet]", *args, **kwargs, file=sys.stderr)