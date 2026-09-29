def alias_for(reseller_id: str) -> str:
    """Return a privacy-safe alias for a reseller ID."""
    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(text: str, reseller_names: list[str]) -> bool:
    """Return False if any non-empty raw reseller name appears verbatim in text."""
    return all(name not in text for name in reseller_names if name)
