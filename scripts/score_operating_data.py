import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path, rows, fields):
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(value):
    try:
        return float(value)
    except ValueError:
        return 0.0


products = read_csv(DATA / "entities.csv")
daily_metrics = read_csv(DATA / "daily_metrics.csv")
events = read_csv(DATA / "source_events.csv")
actions = read_csv(DATA / "recommended_actions.csv")
requirements = read_csv(DATA / "requirements_traceability.csv")
lineage = read_csv(DATA / "lineage_map.csv")
quality = read_csv(DATA / "quality_checks.csv")

metrics_by_product = defaultdict(lambda: {"rows": 0, "quality": 0.0, "freshness": 0.0, "adoption": 0.0, "incidents": 0.0})
for row in daily_metrics:
    bucket = metrics_by_product[row["product_id"]]
    bucket["rows"] += 1
    bucket["quality"] += number(row["quality_score"])
    bucket["freshness"] += number(row["freshness_sla_pct"])
    bucket["adoption"] += number(row["stakeholder_adoption"])
    bucket["incidents"] += number(row["incident_count"])

event_impact = defaultdict(float)
event_count = defaultdict(int)
for row in events:
    event_impact[row["product_id"]] += number(row["estimated_decision_impact"])
    event_count[row["product_id"]] += 1

action_lift = defaultdict(float)
action_effort = defaultdict(float)
for row in actions:
    action_lift[row["product_id"]] += number(row["expected_quality_lift"])
    action_effort[row["product_id"]] += number(row["effort_points"])

requirement_summary = defaultdict(lambda: {"total": 0, "blocked": 0, "validated": 0})
for row in requirements:
    summary = requirement_summary[row["product_id"]]
    summary["total"] += 1
    if row["status"] in {"Blocked", "At risk"}:
        summary["blocked"] += 1
    if row["validation_state"] == "Accepted":
        summary["validated"] += 1

lineage_summary = defaultdict(lambda: {"critical": 0, "dependencies": 0})
for row in lineage:
    summary = lineage_summary[row["product_id"]]
    summary["dependencies"] += 1
    if row["dependency_tier"] == "Critical":
        summary["critical"] += 1

quality_summary = defaultdict(lambda: {"failed": 0, "warning": 0, "checks": 0})
for row in quality:
    summary = quality_summary[row["product_id"]]
    summary["checks"] += 1
    if row["result"] == "Fail":
        summary["failed"] += 1
    if row["result"] == "Warning":
        summary["warning"] += 1

priority_rows = []
for product in products:
    product_id = product["product_id"]
    metrics = metrics_by_product[product_id]
    rows = max(metrics["rows"], 1)
    avg_quality = metrics["quality"] / rows
    avg_freshness = metrics["freshness"] / rows
    avg_adoption = metrics["adoption"] / rows
    avg_incidents = metrics["incidents"] / rows
    req = requirement_summary[product_id]
    dep = lineage_summary[product_id]
    checks = quality_summary[product_id]
    criticality = number(product["criticality"])
    blocker_penalty = req["blocked"] * 6
    quality_gap = max(0, 96 - avg_quality)
    freshness_gap = max(0, 95 - avg_freshness)
    lineage_penalty = dep["critical"] * 3
    incident_penalty = avg_incidents * 5
    impact_score = event_impact[product_id] / 95000
    readiness_score = max(0, 100 - quality_gap - freshness_gap - blocker_penalty - lineage_penalty - incident_penalty)
    priority_score = (
        criticality * 12
        + quality_gap * 1.15
        + freshness_gap * 0.9
        + blocker_penalty
        + lineage_penalty
        + incident_penalty
        + impact_score
    )
    release_lane = "Remediate before release"
    if readiness_score >= 82 and req["blocked"] == 0 and checks["failed"] == 0:
        release_lane = "Release ready"
    elif readiness_score >= 68:
        release_lane = "Validate with stakeholders"
    priority_rows.append(
        {
            "product_id": product_id,
            "product_name": product["product_name"],
            "domain": product["domain"],
            "owner": product["owner"],
            "criticality": product["criticality"],
            "priority_score": f"{priority_score:.1f}",
            "readiness_score": f"{readiness_score:.1f}",
            "avg_quality_score": f"{avg_quality:.1f}",
            "avg_freshness_sla_pct": f"{avg_freshness:.1f}",
            "avg_stakeholder_adoption": f"{avg_adoption:.1f}",
            "open_requirement_blockers": req["blocked"],
            "accepted_requirements": req["validated"],
            "critical_lineage_dependencies": dep["critical"],
            "failed_quality_checks": checks["failed"],
            "warning_quality_checks": checks["warning"],
            "estimated_decision_impact": f"{event_impact[product_id]:.0f}",
            "recommended_quality_lift": f"{action_lift[product_id]:.1f}",
            "effort_points": f"{action_effort[product_id]:.0f}",
            "release_lane": release_lane,
        }
    )

priority_rows.sort(key=lambda row: float(row["priority_score"]), reverse=True)

write_csv(
    OUTPUTS / "priority_queue.csv",
    priority_rows,
    [
        "product_id",
        "product_name",
        "domain",
        "owner",
        "criticality",
        "priority_score",
        "readiness_score",
        "avg_quality_score",
        "avg_freshness_sla_pct",
        "avg_stakeholder_adoption",
        "open_requirement_blockers",
        "accepted_requirements",
        "critical_lineage_dependencies",
        "failed_quality_checks",
        "warning_quality_checks",
        "estimated_decision_impact",
        "recommended_quality_lift",
        "effort_points",
        "release_lane",
    ],
)

traceability_rows = []
for row in requirements:
    product = next(item for item in products if item["product_id"] == row["product_id"])
    traceability_rows.append(
        {
            "requirement_id": row["requirement_id"],
            "product_name": product["product_name"],
            "stakeholder_group": row["stakeholder_group"],
            "user_story": row["user_story"],
            "acceptance_criteria": row["acceptance_criteria"],
            "status": row["status"],
            "validation_state": row["validation_state"],
            "linked_quality_check": row["linked_quality_check"],
            "release_target": row["release_target"],
        }
    )

write_csv(
    OUTPUTS / "requirements_traceability.csv",
    traceability_rows,
    [
        "requirement_id",
        "product_name",
        "stakeholder_group",
        "user_story",
        "acceptance_criteria",
        "status",
        "validation_state",
        "linked_quality_check",
        "release_target",
    ],
)

lineage_risks = []
for row in lineage:
    product = next(item for item in products if item["product_id"] == row["product_id"])
    related_checks = [check for check in quality if check["product_id"] == row["product_id"] and check["source_system"] == row["source_system"]]
    failed = sum(1 for check in related_checks if check["result"] == "Fail")
    warning = sum(1 for check in related_checks if check["result"] == "Warning")
    lineage_risks.append(
        {
            "product_name": product["product_name"],
            "source_system": row["source_system"],
            "pipeline_stage": row["pipeline_stage"],
            "dependency_tier": row["dependency_tier"],
            "refresh_cadence": row["refresh_cadence"],
            "owner": row["owner"],
            "quality_exceptions": failed + warning,
            "remediation": row["remediation"],
        }
    )

write_csv(
    OUTPUTS / "lineage_quality_risks.csv",
    lineage_risks,
    [
        "product_name",
        "source_system",
        "pipeline_stage",
        "dependency_tier",
        "refresh_cadence",
        "owner",
        "quality_exceptions",
        "remediation",
    ],
)

portfolio_summary = {
    "data_products": len(products),
    "daily_metric_rows": len(daily_metrics),
    "requirements": len(requirements),
    "blocked_requirements": sum(1 for item in requirements if item["status"] in {"Blocked", "At risk"}),
    "lineage_dependencies": len(lineage),
    "quality_checks": len(quality),
    "failed_quality_checks": sum(1 for item in quality if item["result"] == "Fail"),
    "release_ready_products": sum(1 for item in priority_rows if item["release_lane"] == "Release ready"),
    "top_priority_product": priority_rows[0]["product_name"],
    "top_priority_score": priority_rows[0]["priority_score"],
}

with (OUTPUTS / "portfolio_summary.json").open("w") as file:
    json.dump(portfolio_summary, file, indent=2)

print(f"Scored {len(products)} data products.")
print(f"Top priority: {priority_rows[0]['product_name']} with score {priority_rows[0]['priority_score']}.")
print(f"Release ready products: {portfolio_summary['release_ready_products']}.")
