const formatNumber = new Intl.NumberFormat("en-US");
const formatMoney = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function setBar(id, value) {
  document.getElementById(id).style.width = `${Math.min(value, 100)}%`;
}

async function loadDashboard() {
  const [metricsResponse, workflowsResponse, runsResponse] = await Promise.all([
    fetch("/api/v1/metrics"),
    fetch("/api/v1/workflows"),
    fetch("/api/v1/runs?limit=8"),
  ]);
  if (!metricsResponse.ok || !workflowsResponse.ok || !runsResponse.ok) {
    throw new Error("Dashboard data is unavailable.");
  }
  const [metrics, workflows, runs] = await Promise.all([
    metricsResponse.json(),
    workflowsResponse.json(),
    runsResponse.json(),
  ]);

  setText("automation-rate", `${metrics.automation_rate}%`);
  setText("success-rate", `${metrics.success_rate}%`);
  setText("hours-saved", formatNumber.format(metrics.hours_saved));
  setText("savings", formatMoney.format(metrics.estimated_savings));
  setText("sla-value", `${metrics.sla_attainment}%`);
  setText("quality-value", `${metrics.average_quality}%`);
  setText("adoption-value", `${metrics.adoption_users} users`);
  setText("records", formatNumber.format(metrics.records_processed));
  setText("active-workflows", metrics.active_workflows);
  setText("total-runs", metrics.total_runs);
  setText("efficiency", `${metrics.automation_rate}%`);
  setBar("sla-bar", metrics.sla_attainment);
  setBar("quality-bar", metrics.average_quality);
  setBar("adoption-bar", Math.min(metrics.adoption_users * 15, 100));

  document.getElementById("workflow-list").innerHTML = workflows.map((workflow) => {
    const automated = workflow.stages.filter((stage) => stage.automated).length;
    const reduction = Math.round(
      ((workflow.manual_minutes - workflow.automated_minutes) / workflow.manual_minutes) * 100,
    );
    return `
      <div class="workflow">
        <div><h3>${workflow.name}</h3><p>${workflow.owner} · v${workflow.version}</p></div>
        <div class="workflow-stat"><span>STAGES</span><strong>${automated}/${workflow.stages.length} automated</strong></div>
        <div class="workflow-stat"><span>TIME REDUCTION</span><strong>${reduction}%</strong></div>
        <span class="pill">${workflow.status}</span>
      </div>`;
  }).join("");

  document.getElementById("run-list").innerHTML = runs.map((run) => `
    <tr>
      <td>${run.correlation_id}</td>
      <td><span class="run-status ${run.status}">${run.status}</span></td>
      <td>${run.triggered_by}</td>
      <td>${formatNumber.format(run.output_records)}</td>
      <td>${(run.quality_score * 100).toFixed(1)}%</td>
      <td>${formatMoney.format(run.estimated_savings)}</td>
    </tr>`).join("");
}

loadDashboard().catch((error) => {
  document.getElementById("workflow-list").innerHTML = `<p>${error.message}</p>`;
});
