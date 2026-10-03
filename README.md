# Meesho Reseller Growth & Alert Intelligence Pipeline

An end-to-end reseller monitoring pipeline built using Python, SQLite, SQL, deterministic narrative templates, validation guardrails, and a mock agent workflow.

The project connects business data generation, SQL analysis, growth detection, narrative generation, and guarded alert drafting into one repeatable offline pipeline.

---

## Project Workflow

The overall flow is:

**Part 1 → Part 2 → Part 3 → Part 4**

### Part 1 — SQL Business Query Engine

Generates a deterministic reseller/order dataset and calculates verified business metrics using SQLite and SQL.

### Part 2 — Python Guardrail & Growth Detection

Validates the monthly category revenue feed and calculates Month-on-Month (MoM) growth using the required 8% threshold rule.

### Part 3 — Narrative & Privacy Layer

Uses verified values from the earlier parts to create controlled stakeholder narratives using a deterministic template. It also prevents raw reseller names from appearing in the final narrative.

### Part 4 — Agentic Workflow

Combines the earlier parts into a guarded workflow:

**Validate → Calculate → Flag → Sort → Draft Top 3 → Suppress Remaining → Escalate Boundary Cases → Hold for Human Approval**

---

## Workflow Pattern Mapping

The project follows the workflow patterns described in the assignment:

* **Part 1 → Part 2:** mirrors the pattern of **"compute real numbers via SQL first, then hand off to a tested guardrail."**
* **Part 2 → Part 3:** mirrors **"validate and classify first, then narrate only from verified values."**
* **Part 3:** applies a controlled **template-fill and privacy/masking** workflow.
* **Part 4:** mirrors an **"Intake → Validate → Compute → Classify → Report Draft → Human Review"** workflow.

Part 1's `monthly_category_revenue.csv` is the main data hand-off used by Part 2 and Part 4.

---

# Repository Structure

```text
meesho-reseller-pipeline/
│
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
│       └── *.csv
│
├── part2_engine/
│   ├── growth_engine.py
│   ├── test_growth_engine.py
│   └── fixtures/
│       └── *.csv
│
├── part3_narrative/
│   ├── prompt_pack.md
│   ├── narrative_report.md
│   ├── masking.py
│   └── test_masking.py
│
├── part4_agent/
│   ├── agent_spec.md
│   ├── mock_agent_runner.py
│   └── test_mock_agent_runner.py
│
└── README.md
```

## Required Submission Files

The assignment requires the public repository to contain:

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

### Additional Local Testing Files

The following files are included to make local execution and verification easier:

```text
part1_sql/run_queries.py
part3_narrative/test_masking.py
part4_agent/test_mock_agent_runner.py
```

These are helper/testing files and are not additional graded submission requirements.

---

# Requirements

* Python 3.9+
* SQLite
* pytest for automated testing

Install pytest if required:

```powershell
py -m pip install pytest
```

No paid service, external LLM, API key, Gmail, SMTP, or hosted service is required.

---

# Run the Complete Pipeline in Order

All commands below should be executed from the repository root:

```text
D:\YourProjectlocation\meesho-reseller-pipeline
```

---

# Part 1 — Dataset Generation and SQL Analysis

## Step 1: Generate the dataset

Run:

```powershell
py data/generate_dataset.py
```

This creates/regenerates:

```text
data/resellers.csv
data/orders.csv
data/meesho_reseller.db
```

The generator uses a fixed random seed, making the dataset reproducible.

Expected dataset:

* 24 resellers
* 900 orders
* 300 orders for April
* 300 orders for May
* 300 orders for June

## Step 2: Run the Part 1 SQL queries

Run:

```powershell
py part1_sql/run_queries.py
```

This generates the CSV outputs under:

```text
part1_sql/output/
```

The main output used by the downstream pipeline is:

```text
part1_sql/output/monthly_category_revenue.csv
```

This file contains:

```text
month,category,revenue,n_orders
```

with 15 month/category combinations.

### Part 1 output files

The generated output files include:

```text
monthly_category_revenue.csv
region_revenue.csv
top_resellers.csv
never_ordered_resellers.csv
zero_order_count_demo.csv
june_delivered_aov.csv
```

### Part 1 → Part 2 hand-off

The important hand-off is:

```text
Part 1
   ↓
monthly_category_revenue.csv
   ↓
Part 2
```

Part 2 uses this verified monthly category revenue feed for validation and MoM growth calculations.

---

# Part 2 — Growth Detection and Validation

Run the automated Part 2 tests:

```powershell
py -m pytest part2_engine/test_growth_engine.py -vv
```

Expected result:

```text
7 passed
```

Part 2 validates the monthly feed and applies the required growth classification.

### MoM calculation

The formula is:

```text
((current_revenue - previous_revenue) / previous_revenue) × 100
```

The result is rounded to two decimal places.

### Flagging rule

The threshold is 8%.

```text
abs(MoM) > 8%   → flagged
abs(MoM) < 8%   → not_flagged
abs(MoM) = 8%   → escalate_exact_boundary
```

### Part 2 tests cover

* Required May MoM calculation
* Required June MoM calculation
* Exact 8% boundary
* Corrupted feed validation
* Valid Part 1 feed validation
* Complete May-vs-April MoM table
* Complete June-vs-May MoM table

---

# Part 3 — Narrative and Privacy Layer

Part 3 is intentionally deterministic and works offline.

Required files:

```text
part3_narrative/prompt_pack.md
part3_narrative/narrative_report.md
part3_narrative/masking.py
```

## Prompt Pack

`prompt_pack.md` contains the required sections:

```text
Trigger
Input list
Prompt
Checklist
```

The checklist contains concrete validation checks for:

* Number integrity
* Fact vs hypothesis
* Correct period/category
* Actionability
* No fabricated information
* Privacy/masking

## Narrative Report

The worked narratives include:

* May — Ethnic Wear: **+77.1%**
* June — Ethnic Wear: **-58.74%**

The narratives follow:

```text
Context → Insight → Implication
```

Facts and hypotheses are explicitly identified.

No unsupported business numbers are invented.

## Privacy masking

Raw reseller names are not exposed in the final reseller narrative.

For example:

```text
RS019 → ALIAS-19
RS006 → ALIAS-06
```

The masking helper verifies that raw reseller names do not leak into the final narrative.

### Optional Part 3 test

Run:

```powershell
py -m pytest part3_narrative/test_masking.py -vv
```

Expected result:

```text
4 passed
```

This is a local verification test and is not an additional assignment submission requirement.

---

# Part 4 — Agentic Workflow

Part 4 combines Parts 1–3 into a guarded, repeatable workflow.

Required files:

```text
part4_agent/agent_spec.md
part4_agent/mock_agent_runner.py
```

The mock agent:

1. Loads the previous and current monthly feeds.
2. Validates the feeds using Part 2's `validate_feed()`.
3. Hard-stops if validation fails.
4. Calculates MoM using Part 2's `mom_growth()`.
5. Classifies each category using Part 2's `is_flagged()`.
6. Sorts flagged categories by absolute MoM percentage in descending order.
7. Drafts messages for at most the top 3 flagged categories.
8. Suppresses remaining flagged categories for manual review.
9. Escalates exact 8% boundary cases without drafting them.
10. Returns one structured JSON result.

Part 4 imports and reuses the Part 2 functions without re-implementing them.

Part 4 also uses the Part 3 template-fill logic for drafted messages.

---

## Part 4 Guardrails

### Input Guardrail

`validate_feed()` must pass before MoM calculation or drafting starts.

If validation fails:

```text
validation_status = "invalid"
action_taken = "hard_stop"
```

Validation errors are surfaced and no MoM calculation is attempted.

### Action Guardrail

The agent does not automatically send messages.

It only creates drafts and holds them for human approval.

```text
drafted_and_held_for_approval
```

### Output Guardrail

Every number in a drafted message must trace back to verified Part 1 or Part 2 values.

The narrative template must not invent additional business figures.

---

## Part 4 Structured Output

The runner returns:

```text
run_month
validation_status
validation_errors
flagged_categories
suppressed_categories
escalated_categories
action_taken
```

The output supports human review rather than automatic message sending.

---

# Part 4 Verification

Run:

```powershell
py -m pytest part4_agent/test_mock_agent_runner.py -vv
```

Expected result:

```text
5 passed
```

The tests cover:

* May scenario — April → May
* June scenario — May → June
* Corrupted current feed → Hard Stop
* Three-message drafting cap
* Exact 8% boundary → escalation

---

# Step-by-Step Final Verification

Before submission, run the following from the repository root.

## 1. Regenerate the dataset

```powershell
py data/generate_dataset.py
```

## 2. Generate Part 1 outputs

```powershell
py part1_sql/run_queries.py
```

## 3. Run Part 2 tests

```powershell
py -m pytest part2_engine/test_growth_engine.py -vv
```

Expected:

```text
7 passed
```

## 4. Run Part 3 masking tests

```powershell
py -m pytest part3_narrative/test_masking.py -vv
```

Expected:

```text
4 passed
```

## 5. Run Part 4 tests

```powershell
py -m pytest part4_agent/test_mock_agent_runner.py -vv
```

Expected:

```text
5 passed
```

## 6. Check Git status

```powershell
git status
```

Temporary Python/pytest files such as:

```text
__pycache__/
.pytest_cache/
*.pyc
```

should not be committed.

The repository `.gitignore` should exclude these temporary files.

---

# Zero API Keys / Offline Execution

The complete pipeline runs with **zero API keys configured**.

No API key is required for:

* Dataset generation
* SQLite/SQL analysis
* MoM calculation
* Feed validation
* Narrative generation
* Privacy masking
* Agent workflow
* Automated tests

The narrative step is implemented using deterministic offline template-fill logic rather than a live LLM/API.

The Part 4 runner performs drafting and holding only. There is no real network call, email integration, or automatic message sending.

---

# Final Submission Checklist

Before submitting, confirm that the public GitHub repository contains the required files:

```text
data/
├── generate_dataset.py
├── resellers.csv
├── orders.csv
└── meesho_reseller.db

part1_sql/
├── queries.sql
└── output/
    └── *.csv

part2_engine/
├── growth_engine.py
├── test_growth_engine.py
└── fixtures/
    └── *.csv

part3_narrative/
├── prompt_pack.md
├── narrative_report.md
└── masking.py

part4_agent/
├── agent_spec.md
└── mock_agent_runner.py

README.md
```

Optional local testing helpers may also be present:

```text
part1_sql/run_queries.py
part3_narrative/test_masking.py
part4_agent/test_mock_agent_runner.py
```

The assignment requires submission of **only the public GitHub repository link**.

No screenshots, PDFs, or other files need to be submitted separately.

---

# Project Completion Summary

The completed project demonstrates:

```text
Dataset Generation
       ↓
SQL Business Metrics
       ↓
Validated Monthly Revenue Feed
       ↓
MoM Growth Detection
       ↓
8% Threshold Flagging
       ↓
Controlled Narrative
       ↓
Privacy Masking
       ↓
Guarded Agent Workflow
       ↓
Top-3 Drafts + Suppression
       ↓
Human Approval
```

The complete workflow is deterministic, repeatable, testable, and executable offline without API keys.
