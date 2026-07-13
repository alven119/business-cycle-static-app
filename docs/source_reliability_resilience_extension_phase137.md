# Phase 137 NY Fed SCE Official Component Automation

Phase 137 extends the completed Phase 134-136 source-reliability roadmap. It
does not reopen or rewrite the historical Phase 136 consumer-confidence
contract. The exact book role remains the Conference Board Consumer Confidence
Index and remains access-limited unless the user supplies authorized private
data.

## Product Outcome

The private NAS refresh worker now has an official New York Fed Survey of
Consumer Expectations workbook adapter. It validates the workbook sheet,
header, scope, period and numeric schema before storing 11 direct monthly
component series in PostgreSQL:

- job-loss and job-finding expectations
- household income and spending growth expectations
- debt-payment delinquency expectations
- expected credit tightening shares
- expected household financial deterioration and improvement shares

The source-operations page shows each component's Traditional-Chinese name,
latest revised value, and the economic meaning of a higher or lower reading.
These are educational and explanatory observations. They are not aggregated
into a confidence score and do not emit phase evidence or transition
confirmation.

## Source And Temporal Contract

The adapter uses the official NY Fed SCE Chart Data workbook linked by the SCE
Data Bank. The contract records the official landing page, FAQ, release
calendar, download license/attribution page, exact workbook URL, parser version,
artifact checksum and monthly observation date. The current workbook is a
revised-history source beginning in June 2013; Phase 137 does not claim a
historical point-in-time archive.

The raw workbook and normalized CSV are retained only on the private NAS source
artifact volume. They are never written to repository output paths or committed.

## Failure And Recovery

Daily full refresh runs treat OECD consumer confidence and NY Fed SCE as two
independent external official sources. A fetch, schema or database failure for
the SCE workbook produces one governed `NYFED_SCE_CONTEXT` parent failure for
the existing source incident center. A later healthy import closes the incident
and appends a recovery receipt. Partial component availability is shown as
partial rather than neutral or complete.

## Safety Boundaries

- Conference Board exact book-core status remains blocked without authorization.
- NY Fed components are `revised_supporting_only` and explanatory context.
- No arbitrary component composite, numeric weight or threshold is added.
- No candidate/current phase, phase score, rank or winner is emitted.
- No portfolio instruction, backtest execution or prospective registry write is
  introduced.

## Deferred Gap

The authorized Conference Board series remains the only unresolved exact-source
gap for this role. Future work may add a private authorized input lane, but it
must preserve license provenance and cannot retroactively relabel NY Fed, OECD
or University of Michigan data as the exact book concept.
