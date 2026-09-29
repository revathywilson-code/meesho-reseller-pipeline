# Reusable Prompt Pack — Flagged Category Stakeholder Update

## Trigger
Start this prompt only when the category-level `is_flagged` result is exactly `"flagged"`.

## Input list
The prompt requires these placeholder variables:

- `{category}` — flagged category name.
- `{previous_revenue}` — verified revenue for the prior month.
- `{current_revenue}` — verified revenue for the current month.
- `{mom_pct}` — verified month-on-month percentage returned by `mom_growth`.
- `{prev_month}` — prior month name.
- `{month}` — current month name.

All numeric values in the final narrative must come only from these supplied placeholders.

## Prompt
You are writing a short stakeholder update for a regional manager.

Use the following verified inputs exactly as supplied:
- Category: `{category}`
- Prior month: `{prev_month}`
- Current month: `{month}`
- Prior-month revenue: `{previous_revenue}`
- Current-month revenue: `{current_revenue}`
- MoM change: `{mom_pct}%`

Write the update in exactly three sections: **Context → Insight → Implication**.

Context: explain what is being measured and state the comparison period as `{month} vs. {prev_month}`.

Insight: state the verified result as a **Fact**, including the exact `{mom_pct}%` change and the relevant supplied revenue values. Do not round, recalculate, or replace supplied values with new values.

Implication: give one specific, actionable next step for the regional manager. If you propose a possible cause that is not proven by the supplied data, label it explicitly as a **Hypothesis**. Do not present an unverified cause as fact.

Reliability rules:
1. Never state a number that is not one of the supplied placeholder values.
2. Never invent orders, customers, products, prices, percentages, dates, causes, or performance figures.
3. Preserve the supplied category and month names exactly.
4. Keep the wording concise and business-focused; write for a regional manager, not a data engineer.
5. Do not mention internal reseller names. If a reseller must be referenced in a downstream narrative, use only its approved coded alias and region.

## Checklist
Before the draft is used, validate all of the following:

1. **Number integrity:** Every number in the draft matches a supplied placeholder value exactly; no new numeric value has been introduced.
2. **Fact/Hypothesis labeling:** Every verified observation is labeled **Fact**, and every proposed but unproven cause is labeled **Hypothesis**.
3. **Period and category accuracy:** `{category}`, `{prev_month}`, and `{month}` appear correctly, and the comparison is explicitly `{month} vs. {prev_month}`.
4. **Actionability:** The Implication contains at least one specific next action that a regional manager can execute or assign, rather than a vague instruction such as "look into it."
5. **No data fabrication:** The draft contains no invented orders, prices, customers, products, causes, or other figures.
6. **Privacy/masking:** Any reseller reference uses only a coded alias and region; no raw reseller name appears in the text.
