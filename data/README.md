# Data Sources

This folder contains synthetic source-style data for a professional sports league data product stewardship workflow. The data is designed for interview discussion and portfolio demonstration only.

## Generation Method

Run:

```bash
python3 scripts/generate_stewardship_data.py
```

The generator uses a fixed random seed so the portfolio artifact is reproducible. It creates 16 data products across sports league domains, 120 days of operating metrics per product, requirement traceability records, source lineage dependencies, quality checks, stakeholder events, and remediation actions.

## Assumptions

- Products are grouped across club reporting, football operations, fan engagement, media insights, sponsorship analytics, ticketing, player health, and consumer products.
- Pipeline stages follow a cloud data product path: landing, validation, warehouse model, and published product API.
- Quality controls focus on freshness, completeness, schema drift, key uniqueness, and lineage ownership.
- Requirement records model stakeholder interviews, user story creation, acceptance criteria, and validation readiness.
- Events model source exceptions, stakeholder escalations, late feeds, and definition mismatches.

No file contains real organization, club, fan, player, health, or commercial performance data.
