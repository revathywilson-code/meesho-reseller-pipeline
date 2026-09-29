# Part 3 — Reliable AI Narrative & Prompt-Pack Report

## 3.2 Worked narrative report

### May — Ethnic Wear: +77.1% MoM, flagged

**Context**  
This measures **Ethnic Wear revenue for May compared with April**. Verified revenue increased from **INR 104520.77 in April** to **INR 185107.61 in May**.

**Insight — Fact**  
**Fact:** Ethnic Wear revenue grew by **77.1% MoM** in May versus April, which is a flagged change under the Part 2 rule.

**Implication — Action + Hypothesis**  
**Hypothesis:** The increase may be associated with stronger demand, assortment changes, or commercial activity, but the revenue figures alone do not prove the cause. **Action:** Review the April-to-May Ethnic Wear order mix, top-selling products, reseller activity, and any campaign or assortment changes, then use that review to decide whether the May pattern should be repeated or scaled.

#### Refinement checklist — May narrative

- **Specificity — Pass:** The narrative names Ethnic Wear, April and May, and uses the verified 77.1% MoM result and supplied revenue values exactly.
- **Audience fit — Pass:** The wording is framed as a concise business update for a regional manager rather than as a technical explanation of the SQL/Python pipeline.
- **Completeness — Pass:** The block contains Context, a fact-labeled Insight, and an Implication with a hypothesis/action distinction.
- **Actionability — Pass:** The next step names the specific evidence to review—order mix, top-selling products, reseller activity, and campaign/assortment changes—before deciding what to scale.

### June — Ethnic Wear: -58.74% MoM, flagged in the opposite direction

**Context**  
This measures **Ethnic Wear revenue for June compared with May**. Verified revenue fell from **INR 185107.61 in May** to **INR 76371.53 in June**.

**Insight — Fact**  
**Fact:** Ethnic Wear revenue declined by **58.74% MoM** in June versus May, which is a flagged change in the opposite direction from May's growth.

**Implication — Action + Hypothesis**  
**Hypothesis:** The decline may reflect weaker demand, lower reseller activity, assortment changes, or other operational factors, but the revenue figures alone do not establish the cause. **Action:** Compare May and June Ethnic Wear order activity (104 orders in May versus 52 in June), then check product availability, active reseller participation, and campaign/assortment changes to identify the most immediate driver before changing stock or promotional plans.

#### Refinement checklist — June narrative

- **Specificity — Pass:** The narrative names Ethnic Wear, May and June, and uses the verified -58.74% MoM result and supplied revenue/order values exactly.
- **Audience fit — Pass:** The wording focuses on the decision a regional manager needs to make and avoids implementation details.
- **Completeness — Pass:** The block contains Context, a fact-labeled Insight, and an Implication with clearly labeled hypothesis and action.
- **Actionability — Pass:** The next step specifies a May-versus-June order check plus product availability, reseller participation, and campaign/assortment review.

## 3.3 Chart-choice justification

### 1. Which month had the highest total revenue?

**Chart type: Bar chart.** This is a **univariate categorical comparison** of total revenue across three months: April (INR 419417.43), May (INR 444594.25), and June (INR 398055.24). A simple bar chart makes the highest month visible within about 10 seconds, uses a zero-starting y-axis so bar lengths remain visually comparable, avoids 3D distortion, and needs no legend because there is only one series.

### 2. What percentage share does Ethnic Wear represent of April's total revenue?

**Chart type: Pie chart.** This is a **univariate part-to-whole question**: Ethnic Wear contributes INR 104520.77 of April's INR 419417.43, or **24.92%**. A simple 2D pie chart is appropriate for showing share of a single total at one point in time, can label the Ethnic Wear slice directly for fast comprehension, and does not require a y-axis; avoid 3D effects and avoid a legend when direct labels are sufficient.

### 3. How do the four regions compare on total revenue?

**Chart type: Bar chart.** This is a **univariate categorical comparison** of one measure—total revenue—across four regions: North (INR 337125.46), West (INR 333106.33), South (INR 316736.68), and East (INR 275098.45). A zero-starting bar chart gives the regional differences a clear visual baseline, makes the ordering readable within about 10 seconds, avoids 3D distortion, and needs no legend because there is only one series.

## 3.4 Masking policy

External-facing narratives must not expose raw `reseller_name` values. Resellers are referenced only by their region and the coded alias returned by `alias_for()`.

### Final masked top-reseller narrative

Part 1's top-reseller query identified five resellers above the INR 50000 total-spend threshold. The masked narrative is: **West ALIAS-19 generated INR 75295.09 in total spend; West ALIAS-22 generated INR 73882.33; South ALIAS-12 generated INR 69936.46; North ALIAS-06 generated INR 64238.97; and North ALIAS-05 generated INR 61825.02.** These aliases preserve operational traceability without exposing raw reseller names.

### Leakage acceptance checks

- `alias_for("RS019") == "ALIAS-19"`
- `assert_no_raw_names_leak(final_narrative, reseller_names) is True`
- A negative-case test containing the raw name `"Mumbai Reseller 1"` must return `False`.
