# Methodology

## Why This Artifact Uses a Transparent Score

The target workflow calls for analysis, requirements management, data quality, lineage, and stakeholder alignment. A transparent score is more appropriate than predictive modeling because the interview value is explaining why a product is ready, blocked, or risky.

## Inputs

- Product catalog with owner, domain, consumer group, criticality, and platform stage.
- Daily quality, freshness, adoption, incident, requirement coverage, and value metrics.
- Requirements with user stories, acceptance criteria, linked quality checks, validation state, and release target.
- Lineage dependencies across source systems and pipeline stages.
- Quality checks for publication controls.
- Stakeholder events and estimated decision impact.

## Priority Score

The score increases when a product has:

- Higher business criticality.
- Larger quality gap from the 96 percent readiness target.
- Larger freshness gap from the 95 percent SLA target.
- Open requirement blockers.
- Critical lineage dependencies.
- Higher incident rate.
- Larger estimated stakeholder decision impact.

## Release Lane

- `Release ready`: high readiness, no blockers, and no failed checks.
- `Validate with stakeholders`: moderate readiness and a clear path to acceptance.
- `Remediate before release`: material quality, lineage, or requirement risk.

## Limitations

The model is synthetic and deterministic. It is designed to show analytical reasoning, not to infer real-world performance. In a production setting, thresholds would be calibrated with historical incidents, platform SLAs, governance standards, and stakeholder risk tolerance.
