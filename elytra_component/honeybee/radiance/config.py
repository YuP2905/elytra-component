from __future__ import annotations

from typing import Dict

from .typing import (
    RadianceOptionTuple,
)


RTRACE_OPTIONS: Dict[str, RadianceOptionTuple] = {
    "ab": (2, 3, 6),
    "ad": (512, 2048, 4096),
    "as_": (128, 2048, 4096),
    "ar": (16, 64, 128),
    "aa": (0.25, 0.2, 0.1),
    "dj": (0, 0.5, 1),
    "ds": (0.5, 0.25, 0.05),
    "dt": (0.5, 0.25, 0.15),
    "dc": (0.25, 0.5, 0.75),
    "dr": (0, 1, 3),
    "dp": (64, 256, 512),
    "st": (0.85, 0.5, 0.15),
    "lr": (4, 6, 8),
    "lw": (0.05, 0.01, 0.005),
    "ss": (0, 0.7, 1),
}

RPICT_OPTIONS: Dict[str, RadianceOptionTuple] = {
    "ab": (2, 3, 6),
    "ad": (512, 2048, 4096),
    "as_": (128, 2048, 4096),
    "ar": (16, 64, 128),
    "aa": (0.25, 0.2, 0.1),
    "ps": (8, 4, 2),
    "pt": (0.15, 0.10, 0.05),
    "pj": (0.6, 0.9, 0.9),
    "dj": (0, 0.5, 1),
    "ds": (0.5, 0.25, 0.05),
    "dt": (0.5, 0.25, 0.15),
    "dc": (0.25, 0.5, 0.75),
    "dr": (0, 1, 3),
    "dp": (64, 256, 512),
    "st": (0.85, 0.5, 0.15),
    "lr": (4, 6, 8),
    "lw": (0.05, 0.01, 0.005),
    "ss": (0, 0.7, 1),
}

RFLUXMTX_OPTIONS: Dict[str, RadianceOptionTuple] = {
    "ab": (3, 5, 6),
    "ad": (5000, 15000, 25000),
    "as_": (128, 2048, 4096),
    "ds": (0.5, 0.25, 0.05),
    "dt": (0.5, 0.25, 0.15),
    "dc": (0.25, 0.5, 0.75),
    "dr": (0, 1, 3),
    "dp": (64, 256, 512),
    "st": (0.85, 0.5, 0.15),
    "lr": (4, 6, 8),
    "lw": (0.000002, 0.000000667, 0.0000004),
    "ss": (0, 0.7, 1),
    "c": (1, 1, 1),
}

RECIPE_TYPES: Dict[str, str] = {
    "0": "rtrace",
    "point-in-time-grid": "rtrace",
    "daylight-factor": "rtrace",
    "rtrace": "rtrace",
    "1": "rpict",
    "point-in-time-image": "rpict",
    "rpict": "rpict",
    "2": "rfluxmtx",
    "annual": "rfluxmtx",
    "rfluxmtx": "rfluxmtx",
}

DETAIL_LEVELS: Dict[str, int] = {
    "0": 0,
    "low": 0,
    "1": 1,
    "medium": 1,
    "2": 2,
    "high": 2,
}

RADIANCE_OPTION_MAP: Dict[str, Dict[str, RadianceOptionTuple]] = {
    "rtrace": RTRACE_OPTIONS,
    "rpict": RPICT_OPTIONS,
    "rfluxmtx": RFLUXMTX_OPTIONS,
}

DEFAULT_ANNUAL_DAYLIGHT_THRESHOLDS = "-t 300 -lt 100 -ut 3000"
DEFAULT_ANNUAL_DAYLIGHT_RADIANCE_PARAMETERS = "-ab 2 -ad 5000 -lw 2e-05"
DEFAULT_POINT_IN_TIME_GRID_RADIANCE_PARAMETERS = "-ab 2 -aa 0.1 -ad 2048 -ar 64"