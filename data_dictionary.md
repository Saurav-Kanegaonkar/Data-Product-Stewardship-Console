# Data Dictionary

| Table | Grain | Key fields | Purpose |
|---|---|---|---|
| `entities.csv` | Data product | `product_id`, `product_name`, `domain`, `owner`, `criticality`, `aws_stage` | Catalog of sports league data products and ownership metadata |
| `daily_metrics.csv` | Product by day | `quality_score`, `freshness_sla_pct`, `stakeholder_adoption`, `incident_count` | Daily operating health used for release readiness scoring |
| `source_events.csv` | Event | `event_type`, `severity`, `stakeholder_group`, `estimated_decision_impact` | Stakeholder escalations, late feeds, definition mismatches, and validation exceptions |
| `recommended_actions.csv` | Action | `action_type`, `business_reason`, `expected_quality_lift`, `effort_points` | Remediation candidates for sprint planning and prioritization |
| `requirements_traceability.csv` | Requirement | `user_story`, `acceptance_criteria`, `status`, `validation_state`, `linked_quality_check` | Business and functional requirement traceability from intake to validation |
| `lineage_map.csv` | Product dependency | `source_system`, `pipeline_stage`, `dependency_tier`, `owner`, `remediation` | Source-to-product lineage and dependency ownership |
| `quality_checks.csv` | Quality check | `check_type`, `threshold`, `observed_value`, `result`, `remediation_owner` | Data quality controls for publication readiness |
| `analysis/outputs/priority_queue.csv` | Data product | `priority_score`, `readiness_score`, `release_lane` | Ranked release and remediation queue |
| `analysis/outputs/requirements_traceability.csv` | Requirement | `requirement_id`, `product_name`, `release_target` | Stakeholder-friendly traceability evidence |
| `analysis/outputs/lineage_quality_risks.csv` | Dependency | `quality_exceptions`, `remediation` | Source dependency risk view |
