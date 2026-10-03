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

# Reuse Part 2 functions without modifying them.
from growth_engine import is_flagged, mom_growth, validate_feed  # noqa: E402

# Reuse Part 3 template-fill logic.
from masking import fill_flagged_category_template  # noqa: E402


def _load_feed(csv_path: str) -> Dict[str, Dict[str, str]]:
    """Load category-level monthly revenue rows keyed by category."""

    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        return {
            row["category"]: row
            for row in reader
            if row.get("category", "").strip()
        }


def _build_flagged_item(
    category: str,
    previous_row: Dict[str, str],
    current_row: Dict[str, str],
    month: str,
    prev_month: str,
) -> Dict[str, object]:
    """Build one flagged-category object with a Part 3 stakeholder draft."""

    previous_revenue = float(previous_row["revenue"])
    current_revenue = float(current_row["revenue"])

    # Reuse Part 2 MoM calculation without modification.
    mom_pct = mom_growth(previous_revenue, current_revenue)

    # Reuse Part 3 template-fill logic.
    message = fill_flagged_category_template(
        category=category,
        previous_revenue=previous_revenue,
        current_revenue=current_revenue,
        mom_pct=mom_pct,
        month=month,
        prev_month=prev_month,
    )

    return {
        "category": category,
        "mom_pct": mom_pct,
        "previous_revenue": previous_revenue,
        "current_revenue": current_revenue,
        "drafted": True,
        "message": message,
    }


def run(
    month: str,
    previous_month_csv: str,
    current_month_csv: str,
) -> dict:
    """
    Run the complete Part 4 agent workflow.

    Workflow:
        1. Validate both feeds.
        2. Hard Stop if validation fails.
        3. Load valid feeds.
        4. Calculate MoM for each common category.
        5. Classify each category using is_flagged().
        6. Sort flagged categories by absolute MoM descending.
        7. Draft only the top 3 flagged categories.
        8. Suppress remaining flagged categories.
        9. Escalate exact 8% boundary categories.
        10. Return the required structured JSON object.
    """

    # ---------------------------------------------------------
    # Step 1 — Validate both feeds before any MoM calculation.
    # ---------------------------------------------------------

    current_valid, current_errors = validate_feed(current_month_csv)
    previous_valid, previous_errors = validate_feed(previous_month_csv)

    validation_errors: List[str] = []

    if not current_valid:
        validation_errors.extend(current_errors)

    if not previous_valid:
        validation_errors.extend(previous_errors)

    # ---------------------------------------------------------
    # Step 2 — Hard Stop on invalid input.
    # No MoM calculation or drafting is performed.
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Step 3 — Load validated feeds.
    # ---------------------------------------------------------

    previous_feed = _load_feed(previous_month_csv)
    current_feed = _load_feed(current_month_csv)

    # Only categories available in both verified feeds are evaluated.
    candidate_categories = sorted(
        set(previous_feed) & set(current_feed)
    )

    flagged_candidates = []
    escalated_categories: List[str] = []

    # ---------------------------------------------------------
    # Step 4 — Calculate MoM and classify every category.
    # ---------------------------------------------------------

    for category in candidate_categories:

        previous_revenue = float(previous_feed[category]["revenue"])
        current_revenue = float(current_feed[category]["revenue"])

        # Part 2 function reused unchanged.
        mom_pct = mom_growth(
            previous_revenue,
            current_revenue,
        )

        # Part 2 function reused unchanged.
        status = is_flagged(mom_pct)

        if status == "flagged":
            flagged_candidates.append(
                (category, mom_pct)
            )

        elif status == "escalate_exact_boundary":
            # Exact 8% boundary goes to human review.
            # It is neither drafted nor suppressed.
            escalated_categories.append(category)

    # ---------------------------------------------------------
    # Step 5 — Sort flagged categories by absolute MoM value.
    # Largest movement comes first.
    # ---------------------------------------------------------

    flagged_candidates.sort(
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    # ---------------------------------------------------------
    # Step 6 — Draft at most the top 3 flagged categories.
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Step 7 — Suppress remaining flagged categories.
    # They are recorded for manual review but no message
    # is drafted for them.
    # ---------------------------------------------------------

    suppressed_categories = [
        category
        for category, _ in flagged_candidates[3:]
    ]

    # ---------------------------------------------------------
    # Step 8 — Return exactly the required structured object.
    # ---------------------------------------------------------

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
            "Usage: py part4_agent/mock_agent_runner.py "
            "<month> <previous_month_csv> <current_month_csv>"
        )

    result = run(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()