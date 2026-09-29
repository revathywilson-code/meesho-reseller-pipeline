from masking import alias_for, assert_no_raw_names_leak


TOP_RESELLER_NAMES = [
    "Mumbai Reseller 1",
    "Mumbai Reseller 4",
    "Hyderabad Reseller 6",
    "Lucknow Reseller 6",
    "Jaipur Reseller 5",
]

FINAL_NARRATIVE = (
    "West ALIAS-19 generated INR 75295.09; "
    "West ALIAS-22 generated INR 73882.33; "
    "South ALIAS-12 generated INR 69936.46; "
    "North ALIAS-06 generated INR 64238.97; "
    "North ALIAS-05 generated INR 61825.02."
)


def test_alias_for_rs019():
    assert alias_for("RS019") == "ALIAS-19"


def test_alias_for_rs006():
    assert alias_for("RS006") == "ALIAS-06"


def test_final_narrative_has_no_raw_name_leak():
    assert assert_no_raw_names_leak(FINAL_NARRATIVE, TOP_RESELLER_NAMES) is True


def test_negative_case_detects_raw_name():
    leaked_text = "West ALIAS-19 and Mumbai Reseller 1 were included."
    assert assert_no_raw_names_leak(leaked_text, TOP_RESELLER_NAMES) is False
