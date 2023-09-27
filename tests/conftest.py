from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="module")
def grammar():
    with open(PROJECT_ROOT / "grammar") as fp:
        yield fp.read()
