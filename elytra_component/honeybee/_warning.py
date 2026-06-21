from __future__ import annotations

def warning_filters() -> None:
    """Suppress warning noise emitted by Honeybee Radiance dependencies.

    Args:
        None.

    Returns:
        None.
    """
    import warnings
    warnings.filterwarnings(
        "ignore",
        message=r"invalid escape sequence.*",
        category=SyntaxWarning,
        module=r"honeybee_radiance_command\._command_util",
    )
