"""Where the experiment data live. Set ACCOUNTABLE_DATA to the forge checkout."""
import os
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[2] / "_forge_accountable_experiments"


def data_root() -> Path:
    root = Path(os.environ.get("ACCOUNTABLE_DATA", DEFAULT))
    if not root.exists():
        raise FileNotFoundError(
            f"experiment data not found at {root}; set ACCOUNTABLE_DATA to the "
            "_forge_accountable_experiments checkout"
        )
    return root
