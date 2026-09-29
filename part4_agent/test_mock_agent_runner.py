import csv
import os
import tempfile

from mock_agent_runner import run


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(PROJECT_ROOT, "part2_engine", "fixtures")


EXPECTED_KEYS = {
    "run_month",
    "validation_status",
    "validation_errors",
    "flagged_categories",
    "suppressed_categories",
    "escalated_categories",
    "action_taken",
}


def _fixture(month: str):
    return os.path.join(FIXTURES_DIR, "monthly_category_revenue.csv")


def _write_month_feed(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["month", "category", "revenue", "n_orders"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _rows_for(month: str):
    path = _fixture(month)
    with open(path, "r", newline="", encoding="utf-8") as file:
        return [row for row in csv.DictReader(file) if row["month"] == month]


def test_may_scenario_acceptance():
    with tempfile.TemporaryDirectory() as temp_dir:
        previous = os.path.join(temp_dir, "april.csv")
        current = os.path.join(temp_dir, "may.csv")
        _write_month_feed(_rows_for("April"), previous)
        _write_month_feed(_rows_for("May"), current)

        result = run("May", previous, current)

    assert set(result.keys()) == EXPECTED_KEYS
    assert result["run_month"] == "May"
    assert result["validation_status"] == "valid"
    assert result["validation_errors"] == []
    assert result["escalated_categories"] == []
    assert result["action_taken"] == "drafted_and_held_for_approval"

    flagged = result["flagged_categories"]
    assert [item["category"] for item in flagged] == [
        "Ethnic Wear",
        "Western Wear",
        "Kids Wear",
    ]
    assert [item["mom_pct"] for item in flagged] == [77.1, -23.6, -23.48]
    assert all(item["drafted"] is True for item in flagged)
    assert set(result["suppressed_categories"]) == {
        "Home & Kitchen",
        "Beauty & Personal Care",
    }

    for item in flagged:
        assert item["category"] in item["message"]
        assert f"{item['mom_pct']}%" in item["message"]


def test_june_scenario_acceptance():
    with tempfile.TemporaryDirectory() as temp_dir:
        previous = os.path.join(temp_dir, "may.csv")
        current = os.path.join(temp_dir, "june.csv")
        _write_month_feed(_rows_for("May"), previous)
        _write_month_feed(_rows_for("June"), current)

        result = run("June", previous, current)

    flagged = result["flagged_categories"]
    assert [item["category"] for item in flagged] == [
        "Ethnic Wear",
        "Home & Kitchen",
        "Kids Wear",
    ]
    assert [item["mom_pct"] for item in flagged] == [-58.74, 42.59, 23.9]
    assert result["suppressed_categories"] == ["Western Wear"]
    assert "Beauty & Personal Care" not in result["suppressed_categories"]
    assert all(item["drafted"] is True for item in flagged)
    assert result["escalated_categories"] == []
    assert result["action_taken"] == "drafted_and_held_for_approval"


def test_corrupted_current_feed_hard_stops():
    valid_previous = _fixture("April")
    corrupted = os.path.join(FIXTURES_DIR, "corrupted_feed.csv")

    result = run("July", valid_previous, corrupted)

    assert result["validation_status"] == "invalid"
    assert result["action_taken"] == "hard_stop"
    assert result["validation_errors"] == [
        "line 3: negative revenue (-4200.0) for category=Western Wear",
        "line 4: missing category (month=July)",
        "line 6: missing revenue (category=Home & Kitchen)",
    ]
    assert result["flagged_categories"] == []
    assert result["suppressed_categories"] == []
    assert result["escalated_categories"] == []


def test_three_message_cap_suppresses_lower_magnitude_flagged_categories():
    with tempfile.TemporaryDirectory() as temp_dir:
        previous = os.path.join(temp_dir, "previous.csv")
        current = os.path.join(temp_dir, "current.csv")

        previous_rows = [
            {"month": "Previous", "category": "A", "revenue": "100", "n_orders": "1"},
            {"month": "Previous", "category": "B", "revenue": "100", "n_orders": "1"},
            {"month": "Previous", "category": "C", "revenue": "100", "n_orders": "1"},
            {"month": "Previous", "category": "D", "revenue": "100", "n_orders": "1"},
        ]
        current_rows = [
            {"month": "Current", "category": "A", "revenue": "130", "n_orders": "1"},
            {"month": "Current", "category": "B", "revenue": "125", "n_orders": "1"},
            {"month": "Current", "category": "C", "revenue": "120", "n_orders": "1"},
            {"month": "Current", "category": "D", "revenue": "119", "n_orders": "1"},
        ]
        _write_month_feed(previous_rows, previous)
        _write_month_feed(current_rows, current)

        result = run("Current", previous, current)

    assert [item["category"] for item in result["flagged_categories"]] == [
        "A",
        "B",
        "C",
    ]
    assert result["suppressed_categories"] == ["D"]


def test_exact_boundary_is_escalated_not_drafted_or_suppressed():
    with tempfile.TemporaryDirectory() as temp_dir:
        previous = os.path.join(temp_dir, "previous.csv")
        current = os.path.join(temp_dir, "current.csv")
        previous_rows = [
            {"month": "Previous", "category": "Boundary", "revenue": "100000", "n_orders": "1"}
        ]
        current_rows = [
            {"month": "Current", "category": "Boundary", "revenue": "108000", "n_orders": "1"}
        ]
        _write_month_feed(previous_rows, previous)
        _write_month_feed(current_rows, current)

        result = run("Current", previous, current)

    assert result["flagged_categories"] == []
    assert result["suppressed_categories"] == []
    assert result["escalated_categories"] == ["Boundary"]
