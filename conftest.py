"""Root conftest.py.

Adds the project root to sys.path so that the
``examples`` package (and any other project-level modules) are importable
from within test files.

pytest automatically executes this file before collecting tests, so no
explicit import is needed.
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path (required for `from examples import ...`)
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
