def alias_for(reseller_id: str) -> str:
    """Return a privacy-safe alias for a reseller ID."""
    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(text: str, reseller_names: list[str]) -> bool:
    """Return False if any non-empty raw reseller name appears verbatim in text."""
    return all(name not in text for name in reseller_names if name)


def fill_flagged_category_template(
    *,
    category: str,
    previous_revenue: float,
    current_revenue: float,
    mom_pct: float,
    month: str,
    prev_month: str,
) -> str:
    """Fill the Part 3 stakeholder-update template using verified values."""

    return (
        f"Context: {category} revenue is being compared for "
        f"{month} vs. {prev_month}.\n\n"
        f"Insight — Fact: {category} revenue changed by {mom_pct}% "
        f"month-on-month, from {previous_revenue} in {prev_month} "
        f"to {current_revenue} in {month}.\n\n"
        "Implication — Action: Compare the current and previous month's "
        "order mix and identify the largest operational driver before "
        "deciding on the next response. "
        "Hypothesis: a material mix or demand shift may explain the "
        "movement, but the supplied revenue data alone does not prove a cause."
    )