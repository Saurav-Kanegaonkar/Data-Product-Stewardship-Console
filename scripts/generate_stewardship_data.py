import csv
import random
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

random.seed(17)

domains = [
    "Club Reporting",
    "Football Operations",
    "Fan Engagement",
    "Media Insights",
    "Sponsorship Analytics",
    "Ticketing",
    "Player Health",
    "Consumer Products",
]

owners = [
    "Analytics Product",
    "Data Engineering",
    "League Operations",
    "Club Success",
    "Fan Data Platform",
    "Business Intelligence",
]

source_systems = {
    "Club Reporting": ["club_crm", "club_ticketing", "identity_graph", "data_warehouse"],
    "Football Operations": ["game_event_feed", "tracking_provider", "official_stats", "data_warehouse"],
    "Fan Engagement": ["fan_identity", "email_platform", "app_events", "data_warehouse"],
    "Media Insights": ["streaming_events", "broadcast_logs", "content_catalog", "data_warehouse"],
    "Sponsorship Analytics": ["sponsor_assets", "campaign_delivery", "salesforce", "data_warehouse"],
    "Ticketing": ["ticketing_platform", "club_crm", "secondary_market", "data_warehouse"],
    "Player Health": ["medical_event_feed", "tracking_provider", "workflow_tool", "data_warehouse"],
    "Consumer Products": ["commerce_platform", "inventory_feed", "loyalty_system", "data_warehouse"],
}

product_names = [
    "Club Revenue Health Mart",
    "Game Operations Readiness Feed",
    "Fan Identity Golden Record",
    "Media Engagement Attribution Mart",
    "Sponsor Asset Delivery Product",
    "Ticket Demand Forecast Feed",
    "Player Availability Signal Mart",
    "Merchandise Sell Through Mart",
    "Club Executive Scorecard Layer",
    "Football Insights Feature Store",
    "Consumer Journey Activation Mart",
    "Cross Platform Content Reach Mart",
    "Partnership Renewal Evidence Pack",
    "Club Seat Upgrade Propensity Mart",
    "Responsible Health Reporting Layer",
    "Retail Inventory Exception Feed",
]


def write_csv(path, rows, fields):
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


products = []
for index, name in enumerate(product_names, start=1):
    domain = domains[(index - 1) % len(domains)]
    products.append(
        {
            "product_id": f"DP{index:03d}",
            "product_name": name,
            "domain": domain,
            "owner": owners[(index + 1) % len(owners)],
            "consumer_group": random.choice(["clubs", "league departments", "football staff", "media teams", "commercial teams"]),
            "criticality": random.choice([3, 4, 4, 5]),
            "status": random.choice(["Live", "Release candidate", "Remediation", "Discovery"]),
            "aws_stage": random.choice(["S3 landing", "Glue validation", "Warehouse model", "Data product API"]),
            "primary_kpi": random.choice(["decision latency", "quality pass rate", "adoption", "coverage", "freshness"]),
        }
    )

write_csv(
    DATA / "entities.csv",
    products,
    ["product_id", "product_name", "domain", "owner", "consumer_group", "criticality", "status", "aws_stage", "primary_kpi"],
)

start = date(2026, 1, 1)
daily_rows = []
for product in products:
    quality_base = random.uniform(82, 97) - (5 - int(product["criticality"])) * 1.2
    freshness_base = random.uniform(84, 99)
    adoption_base = random.uniform(48, 86)
    for offset in range(120):
        drift = random.uniform(-4.5, 4.5)
        incident = 1 if random.random() < (0.05 + (100 - quality_base) / 600) else 0
        if product["status"] == "Remediation":
            incident += 1 if random.random() < 0.07 else 0
        daily_rows.append(
            {
                "date": (start + timedelta(days=offset)).isoformat(),
                "product_id": product["product_id"],
                "quality_score": round(max(58, min(100, quality_base + drift - incident * 3.2)), 1),
                "freshness_sla_pct": round(max(62, min(100, freshness_base + random.uniform(-6, 3) - incident * 4.5)), 1),
                "stakeholder_adoption": round(max(20, min(100, adoption_base + offset * 0.08 + random.uniform(-5, 5))), 1),
                "requirement_coverage_pct": round(max(45, min(100, random.uniform(72, 97) - incident * 4)), 1),
                "incident_count": incident,
                "business_value_index": round(random.uniform(58, 97) + int(product["criticality"]) * 3, 1),
            }
        )

write_csv(
    DATA / "daily_metrics.csv",
    daily_rows,
    [
        "date",
        "product_id",
        "quality_score",
        "freshness_sla_pct",
        "stakeholder_adoption",
        "requirement_coverage_pct",
        "incident_count",
        "business_value_index",
    ],
)

event_types = ["stakeholder escalation", "definition mismatch", "late feed", "schema drift", "manual override", "validation exception"]
events = []
for index in range(1, 321):
    product = random.choice(products)
    severity = random.choice(["Low", "Medium", "High", "High" if product["status"] == "Remediation" else "Medium"])
    events.append(
        {
            "event_id": f"EVT{index:04d}",
            "event_date": (start + timedelta(days=random.randint(0, 119))).isoformat(),
            "product_id": product["product_id"],
            "event_type": random.choice(event_types),
            "severity": severity,
            "stakeholder_group": product["consumer_group"],
            "estimated_decision_impact": random.randint(12000, 96000) * (1.5 if severity == "High" else 1),
            "resolution_status": random.choice(["Open", "In review", "Resolved", "Monitoring"]),
        }
    )

write_csv(
    DATA / "source_events.csv",
    events,
    ["event_id", "event_date", "product_id", "event_type", "severity", "stakeholder_group", "estimated_decision_impact", "resolution_status"],
)

action_types = ["define owner", "profile source", "tighten acceptance criteria", "backfill history", "add lineage monitor", "resolve duplicate keys"]
actions = []
for index in range(1, 97):
    product = random.choice(products)
    actions.append(
        {
            "action_id": f"ACT{index:04d}",
            "product_id": product["product_id"],
            "action_type": random.choice(action_types),
            "business_reason": random.choice(
                [
                    "reduce review cycle rework",
                    "restore stakeholder trust",
                    "prepare release validation",
                    "support executive decision pack",
                    "remove handoff ambiguity",
                ]
            ),
            "expected_quality_lift": round(random.uniform(1.5, 8.5), 1),
            "effort_points": random.choice([2, 3, 5, 8, 13]),
            "status": random.choice(["Ready", "Queued", "In progress", "Needs owner"]),
        }
    )

write_csv(
    DATA / "recommended_actions.csv",
    actions,
    ["action_id", "product_id", "action_type", "business_reason", "expected_quality_lift", "effort_points", "status"],
)

requirements = []
requirement_templates = [
    ("As a club analyst, I need consistent identity joins so that club comparison packs use the same fan population.", "Identity match rate is above 97 percent and exceptions are documented."),
    ("As a football operations stakeholder, I need late feed alerts so that game week decisions are not based on stale data.", "Critical feeds land before the published SLA for five consecutive business days."),
    ("As a commercial lead, I need sponsor delivery metrics tied to source lineage so that renewal narratives can be defended.", "Every metric maps to a source field and owner in the lineage register."),
    ("As a product owner, I need requirement status by release lane so that blocked work is visible before sprint planning.", "Blocked requirements have a named owner, blocker reason, and next validation step."),
    ("As an analytics engineer, I need quality gates before publication so that downstream dashboards do not mask failed checks.", "Completeness, freshness, schema, and key uniqueness checks pass or have approved exceptions."),
]
for product in products:
    for item in range(3):
        template = requirement_templates[(item + int(product["product_id"][-2:])) % len(requirement_templates)]
        status = random.choice(["Accepted", "In validation", "At risk", "Blocked", "Ready for build"])
        requirements.append(
            {
                "requirement_id": f"REQ-{product['product_id']}-{item + 1}",
                "product_id": product["product_id"],
                "stakeholder_group": product["consumer_group"],
                "user_story": template[0],
                "acceptance_criteria": template[1],
                "status": status,
                "validation_state": "Accepted" if status == "Accepted" else random.choice(["Pending", "Needs evidence", "Scheduled"]),
                "linked_quality_check": random.choice(["freshness_sla", "completeness", "schema_drift", "key_uniqueness", "lineage_owner"]),
                "release_target": random.choice(["Week 1 validation", "Club pilot", "Executive readout", "Next sprint", "Backlog"]),
            }
        )

write_csv(
    DATA / "requirements_traceability.csv",
    requirements,
    [
        "requirement_id",
        "product_id",
        "stakeholder_group",
        "user_story",
        "acceptance_criteria",
        "status",
        "validation_state",
        "linked_quality_check",
        "release_target",
    ],
)

lineage_rows = []
for product in products:
    systems = source_systems[product["domain"]]
    for index, system in enumerate(systems):
        lineage_rows.append(
            {
                "product_id": product["product_id"],
                "source_system": system,
                "pipeline_stage": ["ingest", "standardize", "semantic model", "published product"][index],
                "dependency_tier": "Critical" if index in {0, 3} else random.choice(["Supporting", "Critical", "Reference"]),
                "refresh_cadence": random.choice(["intra day", "daily", "game week", "weekly"]),
                "owner": random.choice(owners),
                "remediation": random.choice(
                    [
                        "add automated freshness alert",
                        "confirm source owner",
                        "document metric definition",
                        "backfill missing event history",
                        "resolve duplicate natural keys",
                    ]
                ),
            }
        )

write_csv(
    DATA / "lineage_map.csv",
    lineage_rows,
    ["product_id", "source_system", "pipeline_stage", "dependency_tier", "refresh_cadence", "owner", "remediation"],
)

checks = []
check_types = ["freshness_sla", "completeness", "schema_drift", "key_uniqueness", "lineage_owner"]
for product in products:
    for check_type in check_types:
        system = random.choice(source_systems[product["domain"]])
        result = random.choices(["Pass", "Warning", "Fail"], weights=[68, 23, 9], k=1)[0]
        if product["status"] == "Remediation":
            result = random.choices(["Pass", "Warning", "Fail"], weights=[45, 35, 20], k=1)[0]
        checks.append(
            {
                "check_id": f"CHK-{product['product_id']}-{check_type}",
                "product_id": product["product_id"],
                "source_system": system,
                "check_type": check_type,
                "threshold": random.choice(["95 percent", "98 percent", "zero breaking changes", "named accountable owner"]),
                "observed_value": random.choice(["pass", "warning", "1 exception", "2 exceptions", "owner missing"]),
                "result": result,
                "remediation_owner": random.choice(owners),
            }
        )

write_csv(
    DATA / "quality_checks.csv",
    checks,
    ["check_id", "product_id", "source_system", "check_type", "threshold", "observed_value", "result", "remediation_owner"],
)

with (DATA / "synthetic_operating_data.csv").open("w", newline="") as file:
    writer = csv.writer(file, lineterminator="\n")
    writer.writerow(["dataset", "rows", "purpose"])
    writer.writerow(["entities.csv", len(products), "sports league data product catalog"])
    writer.writerow(["daily_metrics.csv", len(daily_rows), "daily quality, freshness, adoption, and incident metrics"])
    writer.writerow(["source_events.csv", len(events), "stakeholder escalations and validation events"])
    writer.writerow(["requirements_traceability.csv", len(requirements), "user stories, acceptance criteria, and release state"])
    writer.writerow(["lineage_map.csv", len(lineage_rows), "source to product dependency map"])
    writer.writerow(["quality_checks.csv", len(checks), "data quality control outcomes"])

subprocess.run([sys.executable, str(ROOT / "scripts" / "score_operating_data.py")], check=True, cwd=ROOT)
print("Generated synthetic stewardship data.")
