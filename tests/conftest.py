from __future__ import annotations

from pathlib import Path
from typing import (
    Optional,
)

import pytest

from honeybee_energy.config import folders as energy_folders
from honeybee_radiance.config import folders as radiance_folders

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_HBJSON = PROJECT_ROOT / "example" / "model" / "baseline.hbjson"
EXAMPLE_EPW = PROJECT_ROOT / "example" / "weather" / "USA_CA_San_Francisco" / "USA_CA_San.Francisco-Presidio.994016_TMYx.epw"


def _configured_openstudio_exe() -> Optional[Path]:
    openstudio_exe = energy_folders.openstudio_exe
    if openstudio_exe is None:
        return None

    openstudio_path = Path(openstudio_exe)
    return openstudio_path if openstudio_path.is_file() else None


def _configured_radiance_bin() -> Optional[Path]:
    radbin_path = radiance_folders.radbin_path
    if radbin_path is None:
        return None

    radiance_bin = Path(radbin_path)
    if not radiance_bin.is_dir():
        return None

    rtrace_file = radiance_bin / "rtrace.exe"
    return radiance_bin if rtrace_file.is_file() else None


@pytest.fixture
def example_hbjson() -> Path:
    assert EXAMPLE_HBJSON.is_file()
    return EXAMPLE_HBJSON


@pytest.fixture
def example_epw() -> Path:
    assert EXAMPLE_EPW.is_file()
    return EXAMPLE_EPW


@pytest.fixture
def require_openstudio() -> None:
    if _configured_openstudio_exe() is None:
        pytest.skip("OpenStudio CLI is not configured for Honeybee Energy.")


@pytest.fixture
def require_radiance() -> None:
    if _configured_radiance_bin() is None:
        pytest.skip("Radiance binaries are not configured for Honeybee Radiance.")
