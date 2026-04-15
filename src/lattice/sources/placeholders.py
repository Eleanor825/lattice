from __future__ import annotations


def fetch_open_source_placeholder(source_name: str, note: str) -> tuple[list[dict[str, object]], list[str]]:
    return [], [f"{source_name} connector is registered but not fully implemented yet: {note}"]
