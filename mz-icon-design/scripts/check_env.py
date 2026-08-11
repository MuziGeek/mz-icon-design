#!/usr/bin/env python3
try:
    import PIL
    print(f"OK Pillow {PIL.__version__}")
except ImportError:
    print("MISSING Pillow; install scripts/requirements.txt in the active environment.")
    raise SystemExit(1)
