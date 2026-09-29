import csv


def mom_growth(previous: float, current: float) -> float:
    """
    Calculate Month-on-Month growth percentage.

    Formula:
        ((current - previous) / previous) * 100

    Result is rounded to 2 decimal places.
    """
    return round((current - previous) / previous * 100, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    """
    Classify MoM growth against a threshold.

    Returns:
        flagged
        not_flagged
        escalate_exact_boundary
    """
    if abs(mom_pct) > threshold:
        return "flagged"

    if abs(mom_pct) < threshold:
        return "not_flagged"

    return "escalate_exact_boundary"


def validate_feed(csv_path: str) -> tuple[bool, list[str]]:
    """
    Validate a month,category,revenue,n_orders CSV feed.

    Validation rules:
    - Blank category -> error
    - Blank revenue -> error
    - Non-numeric revenue -> error
    - Negative revenue -> error

    Returns:
        (True, []) if there are no errors
        (False, errors) otherwise
    """
    errors = []

    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):
            month = row.get("month", "")
            category = row.get("category", "")
            revenue = row.get("revenue", "")

            if not category.strip():
                errors.append(
                    f"line {line_number}: missing category (month={month})"
                )

            if not revenue.strip():
                errors.append(
                    f"line {line_number}: missing revenue "
                    f"(category={category})"
                )
                continue

            try:
                revenue_value = float(revenue)
            except ValueError:
                errors.append(
                    f"line {line_number}: revenue not numeric: {revenue!r}"
                )
                continue

            if revenue_value < 0:
                errors.append(
                    f"line {line_number}: negative revenue "
                    f"({revenue_value}) for category={category}"
                )

    return (False, errors) if errors else (True, [])