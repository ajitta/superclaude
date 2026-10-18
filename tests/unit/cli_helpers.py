"""Helpers for tests that drive the Click CLI through ``CliRunner``.

Not a test module (pytest's default ``python_files`` skips it).
"""


def all_output(result) -> str:
    """stdout + stderr — argparse writes usage errors to stderr."""
    text = result.output or ""
    try:
        text += result.stderr or ""
    except ValueError:  # stderr not captured separately on older Click
        pass
    return text
