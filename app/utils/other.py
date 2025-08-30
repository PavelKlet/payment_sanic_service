from typing import Any


def filter_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """Removes keys with None values from a dictionary"""
    return {k: v for k, v in data.items() if v is not None}
