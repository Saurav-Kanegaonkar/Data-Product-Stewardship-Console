# Analysis Plan

## Goal

Decide which data products should be released, validated with stakeholders, or remediated before publication.

## Steps

1. Build a data product catalog with domain, owner, consumer group, criticality, and platform stage.
2. Aggregate daily operating metrics for quality, freshness, stakeholder adoption, requirement coverage, incidents, and business value.
3. Join stakeholder events to estimate decision impact and identify repeated pain points.
4. Join requirements to count accepted items, blockers, validation gaps, and release targets.
5. Join lineage and quality controls to identify critical dependencies and failed checks.
6. Score each product using transparent rules instead of a black-box model.
7. Produce three outputs: priority queue, requirement traceability layer, and lineage quality risk map.

## Decision Rules

- Products with low readiness, blockers, failed quality checks, or critical lineage dependencies are routed to remediation.
- Products with moderate readiness and no severe blockers are routed to stakeholder validation.
- Products with high readiness, no blockers, and passing controls can move to release.

## Interview Framing

This plan demonstrates how a Data Product Analyst can bridge business analysis and data stewardship: clarify requirements, assess risk, validate quality, and translate technical evidence into release decisions.
