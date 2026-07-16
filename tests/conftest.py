# conftest.py
# Ensures the `src/` package is importable as top-level modules (mirrors the
# sys.path trick main.py performs on itself), so tests can `import main`
# without needing src/ to be installed as a package.
import os
import sys

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.insert(0, os.path.abspath(SRC_DIR))
