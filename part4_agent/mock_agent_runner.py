"""Part 4 mock agent runner: guarded, deterministic, offline workflow."""

from __future__ import annotations

import csv
import json
import os
import sys
from typing import Dict, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PART2_DIR = os.path.join(PROJECT_ROOT, "part2_engine")
PART3_DIR = os.path.join(PROJECT_ROOT, "part3_narrative")

if PART2_DIR not in sys.path:
    sys.path.insert(0, PART2_DIR)
if PART3_DIR not in sys.path:
    sys.path.insert(0, PART3_DIR)

from growth_engine import is_flagged, mom_growth, validate_feed  # noqa: E402


def fill_flagged_category_template(
    *,
    category: str,
    previous_revenue: float,
    current_revenue: float,
    mom_pct: float,
    month: str,
    prev_month: str,
) -> str:
    """Render Part 3's prompt-pack structure without an LLM or network call."""
    return (
        f"Context: {category} revenue is being compared for {month} vs. {prev_month}.\n\n"
        f"Insight — Fact: {category} revenue changed by {mom_pct}% month-on-month, "
        f"from {previous_revenue} in {prev_month} to {current_revenue} in {month}.\n\n"
        "Implication — Action: Compare the current and previous month's order mix and "
        "identify the largest operational driver before deciding on the next response. "
        "Hypothesis: a material mix or demand shift may explain the movement, but the supplied "
        "revenue data alone does not prove a cause."
    )


def _load_feed(csv_path: str) -> Dict[str, Dict[str, str]]:
    """Load category-level monthly revenue rows keyed by category."""
    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return {row["category"]: row for row in reader if row.get("category", "").strip()}


def _build_flagged_item(
    category: str,
    previous_row: Dict[str, str],
    current_row: Dict[str, str],
    month: str,
    prev_month: str,
) -> Dict[str, object]:
    previous_revenue = float(previous_row["revenue"])
    current_revenue = float(current_row["revenue"])
    mom_pct = mom_growth(previous_revenue, current_revenue)

    return {
        "category": category,
        "mom_pct": mom_pct,
        "previous_revenue": previous_revenue,
        "current_revenue": current_revenue,
        "drafted": True,
        "message": fill_flagged_category_template(
            category=category,
            previous_revenue=previous_revenue,
            current_revenue=current_revenue,
            mom_pct=mom_pct,
            month=month,
            prev_month=prev_month,
        ),
    }


def run(month: str, previous_month_csv: str, current_month_csv: str) -> dict:
    """Run the complete Part 4 workflow and return the structured JSON object."""
    # (1) Validate current and previous feeds before any MoM computation.
    current_valid, current_errors = validate_feed(current_month_csv)
    previous_valid, previous_errors = validate_feed(previous_month_csv)

    validation_errors: List[str] = []
    if not current_valid:
        validation_errors.extend(current_errors)
    if not previous_valid:
        validation_errors.extend(previous_errors)

    # (2) Hard Stop on invalid input; no MoM computation is attempted.
    if validation_errors:
        return {
            "run_month": month,
            "validation_status": "invalid",
            "validation_errors": validation_errors,
            "flagged_categories": [],
            "suppressed_categories": [],
            "escalated_categories": [],
            "action_taken": "hard_stop",
        }

    # (3) Load verified feeds and compute MoM for every category.
    previous_feed = _load_feed(previous_month_csv)
    current_feed = _load_feed(current_month_csv)

    candidate_categories = sorted(set(previous_feed) & set(current_feed))
    flagged_candidates = []
    escalated_categories: List[str] = []

    # (4) Run is_flagged on every category.
    for category in candidate_categories:
        previous_revenue = float(previous_feed[category]["revenue"])
        current_revenue = float(current_feed[category]["revenue"])
        mom_pct = mom_growth(previous_revenue, current_revenue)
        status = is_flagged(mom_pct)

        if status == "flagged":
            flagged_candidates.append((category, mom_pct))
        elif status == "escalate_exact_boundary":
            # (7b) Human escalation only; never draft or suppress.
            escalated_categories.append(category)

    # (5) Sort flagged categories by absolute MoM magnitude descending.
    flagged_candidates.sort(key=lambda item: abs(item[1]), reverse=True)

    # (6) Draft at most the top 3 flagged categories.
    top_flagged = flagged_candidates[:3]
    flagged_categories = []
    for category, _ in top_flagged:
        flagged_categories.append(
            _build_flagged_item(
                category=category,
                previous_row=previous_feed[category],
                current_row=current_feed[category],
                month=month,
                prev_month=previous_feed[category]["month"],
            )
        )

    # (7) Suppress remaining flagged categories without drafting a message.
    suppressed_categories = [category for category, _ in flagged_candidates[3:]]

    # (8) Emit exactly the required structured object.
    return {
        "run_month": month,
        "validation_status": "valid",
        "validation_errors": [],
        "flagged_categories": flagged_categories,
        "suppressed_categories": suppressed_categories,
        "escalated_categories": sorted(escalated_categories),
        "action_taken": "drafted_and_held_for_approval",
    }


def main() -> None:
    """CLI helper for manual execution."""
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: py part4_agent/mock_agent_runner.py <month> "
            "<previous_month_csv> <current_month_csv>"
        )

    result = run(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
