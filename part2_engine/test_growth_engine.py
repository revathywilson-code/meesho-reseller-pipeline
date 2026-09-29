import os

from growth_engine import (
    mom_growth,
    is_flagged,
    validate_feed,
)


FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fixtures"
)


def test_april_to_may_ethnic_wear():
    # GIVEN April -> May Ethnic Wear revenue
    previous = 104520.77
    current = 185107.61

    # WHEN MoM growth is calculated
    mom_pct = mom_growth(previous, current)

    # THEN growth is 77.1% and it is flagged
    assert mom_pct == 77.1
    assert is_flagged(mom_pct) == "flagged"


def test_may_to_june_beauty_personal_care():
    # GIVEN May -> June Beauty & Personal Care revenue
    previous = 35542.11
    current = 37559.07

    # WHEN MoM growth is calculated
    mom_pct = mom_growth(previous, current)

    # THEN growth is 5.67% and it is not flagged
    assert mom_pct == 5.67
    assert is_flagged(mom_pct) == "not_flagged"


def test_exact_threshold_boundary():
    # GIVEN previous = 100000 and current = 108000
    previous = 100000
    current = 108000

    # WHEN MoM growth is calculated
    mom_pct = mom_growth(previous, current)

    # THEN exactly 8% must escalate for human review
    assert mom_pct == 8.0
    assert is_flagged(mom_pct) == "escalate_exact_boundary"


def test_corrupted_feed():
    # GIVEN a corrupted CSV feed
    csv_path = os.path.join(
        FIXTURES_DIR,
        "corrupted_feed.csv"
    )

    # WHEN the feed is validated
    valid, errors = validate_feed(csv_path)

    # THEN validation fails with exactly 3 errors
    assert valid is False

    assert errors == [
        "line 3: negative revenue (-4200.0) for category=Western Wear",
        "line 4: missing category (month=July)",
        "line 6: missing revenue (category=Home & Kitchen)",
    ]


def test_valid_monthly_category_feed():
    # GIVEN the validated Part 1 monthly revenue CSV
    csv_path = os.path.join(
        FIXTURES_DIR,
        "monthly_category_revenue.csv"
    )

    # WHEN the feed is validated
    valid, errors = validate_feed(csv_path)

    # THEN all 15 rows must pass
    assert valid is True
    assert errors == []

def test_may_vs_april_full_mom_table():
    # GIVEN the required April -> May revenue values
    data = {
        "Ethnic Wear": (104520.77, 185107.61),
        "Western Wear": (120000.00, 91680.00),
        "Kids Wear": (100000.00, 76520.00),
        "Home & Kitchen": (100000.00, 90750.00),
        "Beauty & Personal Care": (100000.00, 87250.00),
    }

    expected = {
        "Ethnic Wear": (77.1, "flagged"),
        "Western Wear": (-23.6, "flagged"),
        "Kids Wear": (-23.48, "flagged"),
        "Home & Kitchen": (-9.25, "flagged"),
        "Beauty & Personal Care": (-12.75, "flagged"),
    }

    # WHEN each category's MoM growth is calculated
    # THEN the expected growth and flag status must match
    for category, (previous, current) in data.items():
        mom_pct = mom_growth(previous, current)

        assert mom_pct == expected[category][0]
        assert is_flagged(mom_pct) == expected[category][1]

def test_june_vs_may_full_mom_table():
    # GIVEN the required May -> June revenue values
    data = {
        "Ethnic Wear": (100000.00, 41260.00),
        "Western Wear": (100000.00, 111970.00),
        "Kids Wear": (100000.00, 123900.00),
        "Home & Kitchen": (100000.00, 142590.00),
        "Beauty & Personal Care": (35542.11, 37559.07),
    }

    expected = {
        "Ethnic Wear": (-58.74, "flagged"),
        "Western Wear": (11.97, "flagged"),
        "Kids Wear": (23.9, "flagged"),
        "Home & Kitchen": (42.59, "flagged"),
        "Beauty & Personal Care": (5.67, "not_flagged"),
    }

    # WHEN each category's MoM growth is calculated
    # THEN the expected growth and flag status must match
    for category, (previous, current) in data.items():
        mom_pct = mom_growth(previous, current)

        assert mom_pct == expected[category][0]
        assert is_flagged(mom_pct) == expected[category][1]