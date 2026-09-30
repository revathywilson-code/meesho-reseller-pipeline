# Meesho Reseller Growth & Alert Intelligence Pipeline

A small end-to-end reseller monitoring pipeline built with Python, SQLite, SQL, deterministic narrative templates, validation guardrails, and a mock agent runner.

## Project Workflow

The pipeline connects all four Parts into one repeatable flow:

**Part 1 → Part 2 → Part 3 → Part 4**

- **Part 1 — SQL Business Query Engine:** compute verified business metrics from the seeded SQLite dataset.
- **Part 2 — Python Guardrail & Growth Detection:** validate the Part 1 monthly feed and apply the explicit 8% MoM flagging rule.
- **Part 3 — Reliable AI Narrative:** convert verified flagged-category numbers into a controlled stakeholder narrative without inventing figures or exposing raw reseller names.
- **Part 4 — Agentic Workflow:** validate the feed, calculate MoM changes, flag categories, cap drafted notifications at three, suppress additional flagged categories, handle exact-boundary escalation, and hold all drafts for human approval.

This mirrors the workflow pattern:

> **Part 1 → Part 2** mirrors “compute real numbers via SQL first, then hand off to a tested guardrail.”

> **Part 2 → Part 3** mirrors “validate and classify first, then narrate only from verified values.”

> **Part 4** mirrors an “Intake → Validate → Compute → Classify → Report Draft → Human Review” workflow.

## Repository Structure

```text
meesho-reseller-pipeline/
├── data/
│   ├── generate_dataset.py
│   ├── resellers.csv
│   ├── orders.csv
│   └── meesho_reseller.db
│
├── part1_sql/
│   ├── queries.sql
│   ├── run_queries.py
│   └── output/
│       ├── monthly_category_revenue.csv
│       ├── region_revenue.csv
│       ├── top_resellers.csv
│       ├── never_ordered_resellers.csv
│       ├── zero_order_count_demo.csv
│       └── june_delivered_aov.csv
│
├── part2_engine/
│   ├── growth_engine.py
│   ├── test_growth_engine.py
│   └── fixtures/
│       ├── corrupted_feed.csv
│       └── monthly_category_revenue.csv
│
├── part3_narrative/
│   ├── prompt_pack.md
│   ├── narrative_report.md
│   └── masking.py
│
├── part4_agent/
│   ├── agent_spec.md
│   ├── mock_agent_runner.py
│   └── test_mock_agent_runner.py
│
└── README.md
```
## Extra helper/testing files
The repository may also contain these files. They are not explicitly required by the submission checklist; they are included only to make the project easier to execute, verify, and test locally:
```text
part1_sql/run_queries.py
part3_narrative/test_masking.py
part4_agent/test_mock_agent_runner.py
```
`part1_sql/run_queries.py` is a convenience script for generating the Part 1 CSV outputs.
`part3_narrative/test_masking.py` verifies the reseller-alias masking behavior.
`part4_agent/test_mock_agent_runner.py` verifies the mock-agent acceptance scenarios.
These files are for local execution/testing support and are not additional graded requirements.

## Requirements

- Python 3.9+
- `pytest`

Install pytest:

```powershell
py -m pip install pytest
```

No API key, paid service, external LLM, Gmail, SMTP, or hosted service is required.

## Run the Pipeline in Order

### Part 1 — Generate the dataset

From the repository root:

```powershell
py data/generate_dataset.py
```

This regenerates:

```text
data/resellers.csv
data/orders.csv
data/meesho_reseller.db
```
# Expected dataset contents:
```text
24 resellers
900 orders
300 orders each for April, May, and June
```

# Verify the generated data

Before writing SQL, verify:
```text
resellers.csv → 24 data rows
orders.csv → 900 data rows
```
```text
April → 300
May   → 300
June  → 300
```

The dataset uses a fixed random seed, so the expected business results remain reproducible.

Run the Part 1 queries:

```powershell
py part1_sql/run_queries.py
```

This creates the CSV outputs under:

```text
part1_sql/output/
```

The most important hand-off file is:

```text
part1_sql/output/monthly_category_revenue.csv
```
It must contain exactly 15 month/category rows.
5 categories × 3 months = 15

That feed is consumed by Part 2.

### Part 2 — Validate and test growth detection

Run the Part 2 tests:

```powershell
py -m pytest part2_engine/test_growth_engine.py -vv
```

The tests cover:

- April → May Ethnic Wear growth
- May → June Beauty & Personal Care growth
- Exact 8% boundary escalation
- Corrupted-feed validation
- Valid Part 1 feed validation
- Full May-vs-April MoM table
- Full June-vs-May MoM table

Expected result:

```text
7 passed
```

### Part 3 — Review the narrative layer

Part 3 is intentionally deterministic and offline.

The deliverables are:

```text
part3_narrative/prompt_pack.md
part3_narrative/narrative_report.md
part3_narrative/masking.py
```

The narrative layer:

- uses only supplied verified values;
- follows Context → Insight → Implication;
- labels facts and hypotheses explicitly;
- provides concrete recommendations;
- prevents raw reseller-name leakage by using coded aliases.

Verify that:
`prompt_pack.md` contains Trigger, Input list, Prompt, and Checklist.
`narrative_report.md` contains the May Ethnic Wear +77.1% narrative.
`narrative_report.md` contains the June Ethnic Wear -58.74% narrative.
All 3 chart-choice questions are answered in text.
The top-reseller narrative uses aliases instead of raw reseller names.
Optional local masking test:
```powershell
py -m pytest part3_narrative/test_masking.py -vv
```
Expected result:
```text
4 passed
```
This test file is an optional local verification helper and is not explicitly required by the assignment.

### Part 4 — Run the mock agent

Run the Part 4 tests:

```powershell
py -m pytest part4_agent/test_mock_agent_runner.py -vv
```
Verification:
```text
5 passed
```

The tests cover:

- May scenario: April → May
- June scenario: May → June
- Corrupted current-month feed → Hard Stop
- Three-message notification cap
- Exact 8% boundary → escalation

The main verification command is the Part 4 pytest suite above. The runner entry point is:

```python
run(month, previous_month_csv, current_month_csv)
```

The two CSV arguments should contain the previous month's and current month's category-revenue rows respectively.
The runner returns one structured JSON object with:

```text
run_month
validation_status
validation_errors
flagged_categories
suppressed_categories
escalated_categories
action_taken
```

No message is automatically sent. All drafts are held for human approval.

## Guardrails

### Input Guardrail

`validate_feed()` must pass before MoM calculations or drafting begin.

An invalid feed causes:

```text
validation_status = "invalid"
action_taken = "hard_stop"
```

with the validation errors surfaced.

### Action Guardrail

The mock agent never sends a message automatically.

It only creates drafts and marks the action as:

```text
drafted_and_held_for_approval
```

### Output Guardrail

Every number in a drafted message must trace to a verified Part 1 or Part 2 value.

The narrative layer must not invent figures.

Raw reseller names must not appear in an external-facing narrative. Reseller IDs are converted to aliases such as:

```text
RS019 → ALIAS-19
RS006 → ALIAS-06
```

## Zero API Keys

The complete project runs without any API key.

The “AI narrative” step is implemented as a deterministic offline template-fill workflow. A real LLM or external API is not required for any acceptance criterion.

## Final Submission

The graded deliverable is **one public GitHub repository** containing the required project files.

Verify that the repository contains:

```text
data/generate_dataset.py
data/resellers.csv
data/orders.csv
data/meesho_reseller.db

part1_sql/queries.sql (or queries.py)
part1_sql/output/*.csv

part2_engine/growth_engine.py
part2_engine/test_growth_engine.py
part2_engine/fixtures/*.csv

part3_narrative/prompt_pack.md
part3_narrative/narrative_report.md
part3_narrative/masking.py

part4_agent/agent_spec.md
part4_agent/mock_agent_runner.py

README.md
```

