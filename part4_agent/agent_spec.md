# Part 4 — Agentic Workflow Specification

## 4.1 Agent specification

### Goal
Keep Meesho category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, with every drafted message held for human approval before it is considered sent.

### Tools
The monitoring agent uses these concrete functions:

- `validate_feed(csv_path)` from Part 2 to validate the monthly category revenue feed before any analysis.
- `mom_growth(previous, current)` from Part 2 to compute Month-on-Month revenue change.
- `is_flagged(mom_pct)` from Part 2 to classify each category as `flagged`, `not_flagged`, or `escalate_exact_boundary`.
- `fill_flagged_category_template(...)` from Part 3 to create the deterministic offline stakeholder draft from verified placeholders.

The Part 2 functions are imported and reused unmodified.

### Memory / State
Between runs, the agent needs the prior month's verified revenue for each category, represented by the previous-month CSV. This state allows the next run to calculate MoM change against the correct prior period. The current month's verified category revenue is supplied as the current-month CSV.

### Planner
1. Load the monthly revenue feeds and run `validate_feed`.
2. If either feed is invalid, Hard Stop and surface the validation errors.
3. If valid, compute `mom_growth` for every category present in both feeds.
4. Run `is_flagged` for every category.
5. Sort flagged categories by `abs(mom_pct)` descending.
6. Draft messages for at most the top 3 flagged categories using the Part 3 deterministic template.
7. Record all remaining flagged categories as `suppressed, review manually` without drafting messages.
7b. Record every `escalate_exact_boundary` category in `escalated_categories` without drafting a message.
8. Emit one structured JSON object for the run.

### Feedback Loop
Every drafted message is held for human approval. The runner only reports `action_taken = "drafted_and_held_for_approval"`; it never sends a message and has no Gmail, SMTP, or network integration.

## Guardrails

### Input guardrail
`validate_feed` must pass before any MoM calculation or narrative drafting begins. An invalid feed causes an immediate Hard Stop.

### Action guardrail
No message is ever auto-sent. Drafts are created and held for human approval only.

### Output guardrail
Every numeric value in a drafted message must trace directly to a verified Part 1/Part 2 placeholder value. No invented figures are allowed.

## Success and error stopping conditions

**Success:** the feeds are valid and the agent produces the appropriate top-3 drafts, suppression list, and/or exact-boundary escalation list. A valid run may also produce zero drafts when no category crosses the threshold.

**Error:** `validate_feed` returns `False` for either input feed. The agent performs a Hard Stop, surfaces the validation errors, produces no flagged or suppressed categories, and performs no MoM computation.

## 4.1 Given-When-Then agent specifications

### Scenario 1 — April to May Ethnic Wear
**Given** April→May Ethnic Wear revenue moves from `104520.77` to `185107.61`, **when** the agent runs its MoM and flagging tools on that category, **then** `mom_growth` returns `77.1` and `is_flagged` returns `"flagged"`, so the category is eligible for a drafted notification.

### Scenario 2 — May to June Beauty & Personal Care
**Given** May→June Beauty & Personal Care revenue moves from `35542.11` to `37559.07`, **when** the agent evaluates the category, **then** `mom_growth` returns `5.67` and `is_flagged` returns `"not_flagged"`, so no notification is drafted and the category is not suppressed.

### Scenario 3 — Exact threshold boundary
**Given** a synthetic pair `previous=100000`, `current=108000`, **when** the agent evaluates the pair, **then** `mom_growth` returns exactly `8.0` and `is_flagged` returns `"escalate_exact_boundary"`; the category is escalated for human review and is neither drafted nor treated as not flagged.

### Scenario 4 — Corrupted feed
**Given** the corrupted feed fixture contains the specified negative-revenue, missing-category, and missing-revenue errors, **when** the agent validates the current-month feed, **then** validation fails with those exact three errors, the run is a Hard Stop, and no MoM computation or drafting is attempted.

## 4.3 Structured JSON contract

Every run returns exactly these top-level keys:

- `run_month`
- `validation_status`
- `validation_errors`
- `flagged_categories`
- `suppressed_categories`
- `escalated_categories`
- `action_taken`

Each drafted flagged-category object contains:

- `category`
- `mom_pct`
- `previous_revenue`
- `current_revenue`
- `drafted`
- `message`

`action_taken` is either `"drafted_and_held_for_approval"` for a valid run or `"hard_stop"` for an invalid run.
