"""Text normalisation helpers."""


def normalize(text):
    """Lowercase and strip the input.

    Returns None when the input is empty.
    """
    if not text:
        return "<blank>"
    return text.strip().lower()
