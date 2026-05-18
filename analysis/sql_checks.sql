-- Data product readiness foundation
select
  product_id,
  avg(quality_score) as avg_quality_score,
  avg(freshness_sla_pct) as avg_freshness_sla_pct,
  avg(stakeholder_adoption) as avg_stakeholder_adoption,
  sum(incident_count) as incident_count
from daily_metrics
group by 1
order by avg_quality_score asc;

-- Requirement traceability blockers
select
  product_id,
  count(*) as requirement_count,
  sum(case when status in ('Blocked', 'At risk') then 1 else 0 end) as blocked_or_at_risk,
  sum(case when validation_state = 'Accepted' then 1 else 0 end) as accepted_count
from requirements_traceability
group by 1
order by blocked_or_at_risk desc;

-- Critical lineage dependencies
select
  product_id,
  source_system,
  pipeline_stage,
  dependency_tier,
  owner,
  remediation
from lineage_map
where dependency_tier = 'Critical'
order by product_id, pipeline_stage;

-- Quality gate failures
select
  product_id,
  source_system,
  check_type,
  threshold,
  observed_value,
  remediation_owner
from quality_checks
where result = 'Fail'
order by product_id, check_type;

-- Stewardship priority queue
select
  p.product_id,
  p.product_name,
  p.domain,
  p.priority_score,
  p.readiness_score,
  p.open_requirement_blockers,
  p.failed_quality_checks,
  p.critical_lineage_dependencies,
  p.release_lane
from priority_queue p
order by p.priority_score desc;
