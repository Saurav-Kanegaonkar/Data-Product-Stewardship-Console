const paths = {
  products: "data/entities.csv",
  priority: "analysis/outputs/priority_queue.csv",
  requirements: "analysis/outputs/requirements_traceability.csv",
  lineage: "analysis/outputs/lineage_quality_risks.csv",
  checks: "data/quality_checks.csv",
  summary: "analysis/outputs/portfolio_summary.json",
};

const formatNumber = new Intl.NumberFormat("en-US");
const formatMoney = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function parseCsv(text) {
  const rows = [];
  let field = "";
  let row = [];
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === '"' && quoted && next === '"') {
      field += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (field || row.length) {
        row.push(field);
        rows.push(row);
        row = [];
        field = "";
      }
      if (char === "\r" && next === "\n") index += 1;
    } else {
      field += char;
    }
  }

  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }

  const [headers, ...records] = rows;
  return records.map((record) =>
    Object.fromEntries(headers.map((header, index) => [header, record[index] || ""]))
  );
}

async function loadCsv(path) {
  const response = await fetch(path);
  return parseCsv(await response.text());
}

function number(value) {
  return Number.parseFloat(value) || 0;
}

function laneClass(lane) {
  if (lane === "Release ready") return "ready";
  if (lane === "Validate with stakeholders") return "validate";
  return "remediate";
}

function renderScorecards(summary, priority) {
  const blockedRate = Math.round((summary.blocked_requirements / summary.requirements) * 100);
  const topProduct = priority[0];
  const cards = [
    ["Data products", summary.data_products, "cataloged across league domains"],
    ["Blocked requirements", `${blockedRate}%`, `${summary.blocked_requirements} need owner, evidence, or scope clarity`],
    ["Quality exceptions", summary.failed_quality_checks, "failed checks before release"],
    ["Top priority", topProduct.product_name, `score ${topProduct.priority_score}, ${topProduct.release_lane.toLowerCase()}`],
  ];

  document.querySelector("#scorecards").innerHTML = cards
    .map(
      ([label, value, detail]) => `
        <article>
          <span>${label}</span>
          <strong>${value}</strong>
          <p>${detail}</p>
        </article>
      `
    )
    .join("");
}

function renderStewardship(priority, products) {
  const rows = priority.slice(0, 8);
  const productCount = new Map(products.map((product) => [product.product_id, product]));
  document.querySelector("#surface-stewardship").innerHTML = `
    <div class="surface-grid wide-left">
      <section class="panel">
        <div class="panel-heading">
          <p class="eyebrow">Executive stewardship queue</p>
          <h2>Rank data product risk by business value, quality, lineage, and requirement blockers</h2>
        </div>
        <div class="queue-list">
          ${rows
            .map((row, index) => {
              const product = productCount.get(row.product_id);
              return `
                <article class="queue-item">
                  <div class="rank">${index + 1}</div>
                  <div>
                    <h3>${row.product_name}</h3>
                    <p>${row.domain} · ${row.owner} · ${product.consumer_group}</p>
                    <div class="bar" aria-label="Readiness score">
                      <span style="width:${Math.min(100, number(row.readiness_score))}%"></span>
                    </div>
                  </div>
                  <div class="queue-metrics">
                    <strong>${row.priority_score}</strong>
                    <span class="pill ${laneClass(row.release_lane)}">${row.release_lane}</span>
                  </div>
                </article>
              `;
            })
            .join("")}
        </div>
      </section>
      <aside class="panel decision-card">
        <p class="eyebrow">Decision readout</p>
        <h2>${rows[0].product_name}</h2>
        <dl>
          <div><dt>Readiness</dt><dd>${rows[0].readiness_score}</dd></div>
          <div><dt>Quality</dt><dd>${rows[0].avg_quality_score}</dd></div>
          <div><dt>Freshness SLA</dt><dd>${rows[0].avg_freshness_sla_pct}%</dd></div>
          <div><dt>Decision impact</dt><dd>${formatMoney.format(number(rows[0].estimated_decision_impact))}</dd></div>
        </dl>
        <p class="callout">Recommendation: hold release until blocked acceptance criteria and failed quality checks have named owners, evidence, and a validation date.</p>
      </aside>
    </div>
  `;
}

function renderRequirements(requirements) {
  const visible = requirements.filter((row) => row.status !== "Accepted").slice(0, 9);
  const counts = visible.reduce(
    (acc, row) => {
      acc[row.status] = (acc[row.status] || 0) + 1;
      return acc;
    },
    {}
  );

  document.querySelector("#surface-requirements").innerHTML = `
    <div class="surface-grid split">
      <section class="panel">
        <div class="panel-heading">
          <p class="eyebrow">Requirements traceability</p>
          <h2>Connect stakeholder intent to acceptance criteria, validation evidence, and release targets</h2>
        </div>
        <div class="requirement-board">
          ${visible
            .map(
              (row) => `
                <article class="requirement-card">
                  <div>
                    <span class="tag">${row.requirement_id}</span>
                    <span class="tag muted">${row.status}</span>
                  </div>
                  <h3>${row.product_name}</h3>
                  <p>${row.user_story}</p>
                  <footer>
                    <span>${row.linked_quality_check}</span>
                    <strong>${row.release_target}</strong>
                  </footer>
                </article>
              `
            )
            .join("")}
        </div>
      </section>
      <aside class="panel">
        <p class="eyebrow">Acceptance criteria lens</p>
        <h2>Where clarity is still needed</h2>
        <div class="stacked-stats">
          ${Object.entries(counts)
            .map(([status, count]) => `<div><span>${status}</span><strong>${count}</strong></div>`)
            .join("")}
        </div>
        <div class="criteria-box">
          <span>Example criterion</span>
          <p>${visible[0].acceptance_criteria}</p>
        </div>
        <p class="callout">The workbench shows how a product analyst can prevent vague requests from moving into build without acceptance criteria and validation evidence.</p>
      </aside>
    </div>
  `;
}

function renderLineage(lineage, checks) {
  const topRisks = lineage
    .filter((row) => number(row.quality_exceptions) > 0 || row.dependency_tier === "Critical")
    .slice(0, 10);
  const checkCounts = checks.reduce(
    (acc, row) => {
      acc[row.result] = (acc[row.result] || 0) + 1;
      return acc;
    },
    {}
  );

  document.querySelector("#surface-lineage").innerHTML = `
    <div class="surface-grid wide-right">
      <section class="panel">
        <div class="panel-heading">
          <p class="eyebrow">Lineage and quality controls</p>
          <h2>Validate source dependencies before publishing stakeholder-facing data products</h2>
        </div>
        <table>
          <thead>
            <tr>
              <th>Data product</th>
              <th>Source</th>
              <th>Stage</th>
              <th>Tier</th>
              <th>Exceptions</th>
              <th>Remediation</th>
            </tr>
          </thead>
          <tbody>
            ${topRisks
              .map(
                (row) => `
                  <tr>
                    <td>${row.product_name}</td>
                    <td>${row.source_system}</td>
                    <td>${row.pipeline_stage}</td>
                    <td>${row.dependency_tier}</td>
                    <td>${row.quality_exceptions}</td>
                    <td>${row.remediation}</td>
                  </tr>
                `
              )
              .join("")}
          </tbody>
        </table>
      </section>
      <aside class="panel quality-panel">
        <p class="eyebrow">Control outcomes</p>
        <h2>Quality gate summary</h2>
        <div class="donut" style="--pass:${checkCounts.Pass || 0};--warn:${checkCounts.Warning || 0};--fail:${checkCounts.Fail || 0}">
          <strong>${formatNumber.format(checks.length)}</strong>
          <span>checks</span>
        </div>
        <dl>
          <div><dt>Pass</dt><dd>${checkCounts.Pass || 0}</dd></div>
          <div><dt>Warning</dt><dd>${checkCounts.Warning || 0}</dd></div>
          <div><dt>Fail</dt><dd>${checkCounts.Fail || 0}</dd></div>
        </dl>
        <p class="callout">Every remediation action is tied to a source system, owner, and release risk so technical teams and business stakeholders can align quickly.</p>
      </aside>
    </div>
  `;
}

function bindTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      const tab = button.dataset.tab;
      activateTab(tab);
    });
  });
}

function activateTab(tab) {
  document.querySelectorAll(".tab-button").forEach((item) => item.classList.toggle("active", item.dataset.tab === tab));
  document.querySelectorAll(".surface").forEach((surface) => {
    surface.classList.toggle("active", surface.dataset.surface === tab);
  });
}

async function init() {
  const [products, priority, requirements, lineage, checks, summary] = await Promise.all([
    loadCsv(paths.products),
    loadCsv(paths.priority),
    loadCsv(paths.requirements),
    loadCsv(paths.lineage),
    loadCsv(paths.checks),
    fetch(paths.summary).then((response) => response.json()),
  ]);

  renderScorecards(summary, priority);
  renderStewardship(priority, products);
  renderRequirements(requirements);
  renderLineage(lineage, checks);
  bindTabs();
  const requestedSurface = new URLSearchParams(window.location.search).get("surface");
  if (["stewardship", "requirements", "lineage"].includes(requestedSurface)) {
    activateTab(requestedSurface);
  }
}

init().catch((error) => {
  document.body.innerHTML = `<main class="app-shell"><section class="panel"><h1>Unable to load artifact data</h1><p>${error.message}</p></section></main>`;
});
