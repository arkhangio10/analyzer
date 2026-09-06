/* The QC console.
 *
 * Every number shown here is rendered as text, never interpolated as markup,
 * because source URLs and finding messages travel through records this process
 * did not author. `textContent` throughout is the reason there is no escaping
 * helper to forget to call.
 *
 * The chart is drawn as SVG from the sample series rather than loaded from a
 * charting library: the page has no third-party script, and a reader who views
 * source can see exactly which points were plotted.
 */

(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const form = $("project-form");
  const projectInput = $("project-id");
  const libraryError = $("library-error");
  const libraryPanel = $("library-panel");
  const evidenceNote = $("evidence-note");
  const verdictBlock = $("verdict-block");
  const verdictBody = $("verdict-table").querySelector("tbody");
  const analysisBody = $("analysis-table").querySelector("tbody");
  const libraryEmpty = $("library-empty");

  const detailPanel = $("detail-panel");
  const detailVerdict = $("detail-verdict");
  const detailSource = $("detail-source");
  const detailProvenance = $("detail-provenance");
  const countsBody = $("counts-table").querySelector("tbody");
  const findingsList = $("findings-list");
  const noFindings = $("no-findings");
  const seriesFigure = $("series-figure");
  const noSeries = $("no-series");
  const seriesChart = $("series-chart");
  const seriesCaption = $("series-caption");
  const proveButton = $("prove-button");
  const proveResult = $("prove-result");
  const proveHeadline = $("prove-headline");
  const proveStages = $("prove-stages");
  const detailError = $("detail-error");

  const SVG_NS = "http://www.w3.org/2000/svg";
  const LINE_COLOURS = [
    "#6558f5", "#1c6b3a", "#9a2020", "#8a5a00",
    "#26667f", "#7a2f7a", "#3f6212", "#8a3324",
  ];

  let currentProject = "";
  let currentExtraction = "";

  function showError(node, message) {
    node.textContent = message;
    node.hidden = false;
  }

  function clearError(node) {
    node.textContent = "";
    node.hidden = true;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function cell(row, text, className) {
    const td = document.createElement("td");
    td.textContent = text;
    if (className) td.className = className;
    row.appendChild(td);
    return td;
  }

  async function getJson(url, options) {
    const response = await fetch(url, options);
    let body = null;
    try {
      body = await response.json();
    } catch (error) {
      body = null;
    }
    if (!response.ok) {
      const detail = body && body.detail ? body.detail : `Request failed (${response.status}).`;
      throw new Error(detail);
    }
    return body;
  }

  // --- library --------------------------------------------------------

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const projectId = projectInput.value.trim();
    if (!projectId) return;
    clearError(libraryError);
    detailPanel.hidden = true;
    try {
      const view = await getJson(
        `/api/qc/projects/${encodeURIComponent(projectId)}/library`
      );
      currentProject = projectId;
      renderLibrary(view);
    } catch (error) {
      libraryPanel.hidden = true;
      showError(libraryError, error.message);
    }
  });

  function renderLibrary(view) {
    evidenceNote.textContent = view.evidence_note;

    clear(verdictBody);
    verdictBlock.hidden = !view.evidence_available || view.verdicts.length === 0;
    view.verdicts.forEach((row) => {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      const badge = document.createElement("span");
      badge.className = "verdict";
      badge.dataset.verdict = row.verdict;
      badge.textContent = row.verdict;
      td.appendChild(badge);
      tr.appendChild(td);
      cell(tr, String(row.analyses));
      cell(tr, String(row.samples));
      cell(tr, String(row.tokens));
      verdictBody.appendChild(tr);
    });

    clear(analysisBody);
    libraryEmpty.hidden = view.analyses.length > 0;
    view.analyses.forEach((item) => {
      const tr = document.createElement("tr");
      const verdictCell = document.createElement("td");
      const badge = document.createElement("span");
      badge.className = "verdict";
      badge.dataset.verdict = item.verdict;
      badge.textContent = item.verdict;
      verdictCell.appendChild(badge);
      tr.appendChild(verdictCell);

      cell(tr, item.source_url || "(no source recorded)", "wrap");
      cell(tr, String(item.sample_count));
      cell(tr, String(item.distinct_joint_count));
      cell(tr, new Date(item.created_at).toLocaleString());

      const actionCell = document.createElement("td");
      const open = document.createElement("button");
      open.type = "button";
      open.textContent = "Inspect";
      open.addEventListener("click", () => {
        Array.from(analysisBody.querySelectorAll("tr")).forEach((row) =>
          row.classList.remove("selected")
        );
        tr.classList.add("selected");
        openAsset(item.analysis_id, item.extraction_id);
      });
      actionCell.appendChild(open);
      tr.appendChild(actionCell);

      analysisBody.appendChild(tr);
    });

    libraryPanel.hidden = false;
  }

  // --- asset detail ---------------------------------------------------

  async function openAsset(analysisId, extractionId) {
    clearError(detailError);
    proveResult.hidden = true;
    try {
      const detail = await getJson(
        `/api/qc/projects/${encodeURIComponent(currentProject)}` +
          `/analyses/${encodeURIComponent(analysisId)}`
      );
      currentExtraction = extractionId;
      renderDetail(detail);
      detailPanel.hidden = false;
      detailPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      showError(detailError, error.message);
      detailPanel.hidden = false;
    }
  }

  function renderDetail(detail) {
    detailVerdict.textContent = detail.verdict;
    detailVerdict.dataset.verdict = detail.verdict;
    detailSource.textContent = detail.source_url || "(no source recorded)";

    detailProvenance.textContent =
      `Claimed by ${detail.provider || "an unrecorded provider"}` +
      `${detail.model_version ? ` (${detail.model_version})` : ""}` +
      ` at a cost of ${detail.cloud_calls_made} cloud call(s).` +
      ` Measurement method: ${detail.measurement_method || "unrecorded"}.` +
      ` Physically measured: ${detail.physically_measured ? "yes" : "no"}.`;

    clear(countsBody);
    const counts = [
      ["Samples returned", detail.sample_count],
      ["Distinct joints", detail.distinct_joint_count],
      ["Observed span (s)", detail.observed_span_seconds.toFixed(2)],
      ["Samples per second", detail.samples_per_second.toFixed(2)],
      ["Mean confidence", detail.mean_confidence.toFixed(3)],
      ["Clear samples", detail.clear_sample_count],
      ["Mirrored frame ratio", detail.mirrored_frame_ratio.toFixed(3)],
      ["Distinct confidence values", detail.distinct_confidence_values],
      ["Distinct visibility values", detail.distinct_visibility_values],
      ["Joints checked for cycles", detail.checked_joint_count],
      [
        "Acyclic joints",
        detail.acyclic_joints.length ? detail.acyclic_joints.join(", ") : "none",
      ],
    ];
    counts.forEach(([label, value]) => {
      const tr = document.createElement("tr");
      const th = document.createElement("th");
      th.scope = "row";
      th.textContent = label;
      tr.appendChild(th);
      cell(tr, String(value), "wrap");
      countsBody.appendChild(tr);
    });

    clear(findingsList);
    noFindings.hidden = detail.findings.length > 0;
    detail.findings.forEach((finding) => {
      const li = document.createElement("li");
      const code = document.createElement("code");
      code.textContent = finding.code;
      li.appendChild(code);
      li.appendChild(document.createTextNode(` ${finding.message}`));
      const pairs = Object.entries(finding.values);
      if (pairs.length) {
        const values = pairs
          .map(([key, value]) => {
            // Audit values are strings by contract; some are words, not numbers.
            const asNumber = Number(value);
            const shown =
              value !== "" && Number.isFinite(asNumber)
                ? String(Number(asNumber.toFixed(3)))
                : value;
            return `${key}=${shown}`;
          })
          .join(", ");
        const small = document.createElement("div");
        small.className = "muted";
        small.textContent = values;
        li.appendChild(small);
      }
      findingsList.appendChild(li);
    });

    drawSeries(detail.series);
  }

  // --- the chart ------------------------------------------------------

  function drawSeries(series) {
    clear(seriesChart);
    const hasPoints = Array.isArray(series) && series.length > 0;
    noSeries.hidden = hasPoints;
    seriesFigure.hidden = !hasPoints;
    if (!hasPoints) {
      seriesCaption.textContent = "";
      return;
    }

    const title = document.createElementNS(SVG_NS, "title");
    title.id = "series-title";
    title.textContent = "Joint angle over time";
    seriesChart.appendChild(title);
    const desc = document.createElementNS(SVG_NS, "desc");
    desc.id = "series-desc";
    desc.textContent =
      `${series.length} retained readings across ` +
      `${new Set(series.map((p) => `${p.side}.${p.joint}`)).size} joint series.`;
    seriesChart.appendChild(desc);

    const width = 720;
    const height = 260;
    const pad = { top: 12, right: 12, bottom: 24, left: 44 };

    const times = series.map((p) => p.t);
    const angles = series.map((p) => p.angle);
    const tMin = Math.min(...times);
    const tMax = Math.max(...times);
    const aMin = Math.min(...angles);
    const aMax = Math.max(...angles);
    const tSpan = tMax - tMin || 1;
    const aSpan = aMax - aMin || 1;

    const x = (t) =>
      pad.left + ((t - tMin) / tSpan) * (width - pad.left - pad.right);
    const y = (a) =>
      height - pad.bottom - ((a - aMin) / aSpan) * (height - pad.top - pad.bottom);

    const axis = document.createElementNS(SVG_NS, "path");
    axis.setAttribute(
      "d",
      `M ${pad.left} ${pad.top} L ${pad.left} ${height - pad.bottom} ` +
        `L ${width - pad.right} ${height - pad.bottom}`
    );
    axis.setAttribute("stroke", "rgba(23,23,23,0.4)");
    axis.setAttribute("fill", "none");
    seriesChart.appendChild(axis);

    [[aMax, pad.top], [aMin, height - pad.bottom]].forEach(([value, at]) => {
      const label = document.createElementNS(SVG_NS, "text");
      label.setAttribute("x", String(pad.left - 6));
      label.setAttribute("y", String(at + 4));
      label.setAttribute("text-anchor", "end");
      label.setAttribute("font-size", "11");
      label.setAttribute("fill", "#3c3c3c");
      label.textContent = value.toFixed(1);
      seriesChart.appendChild(label);
    });

    const grouped = new Map();
    series.forEach((point) => {
      const key = point.side ? `${point.side}.${point.joint}` : point.joint;
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(point);
    });

    let index = 0;
    grouped.forEach((points, key) => {
      points.sort((a, b) => a.t - b.t);
      const d = points
        .map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.t).toFixed(1)} ${y(p.angle).toFixed(1)}`)
        .join(" ");
      const path = document.createElementNS(SVG_NS, "path");
      path.setAttribute("d", d);
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", LINE_COLOURS[index % LINE_COLOURS.length]);
      path.setAttribute("stroke-width", "1.6");
      const label = document.createElementNS(SVG_NS, "title");
      label.textContent = key;
      path.appendChild(label);
      seriesChart.appendChild(path);
      index += 1;
    });

    seriesCaption.textContent =
      `${series.length} readings, ${grouped.size} joint series, ` +
      `${tMin.toFixed(1)}s to ${tMax.toFixed(1)}s, ` +
      `${aMin.toFixed(1)}° to ${aMax.toFixed(1)}°.`;
  }

  // --- prove it -------------------------------------------------------

  proveButton.addEventListener("click", async () => {
    if (!currentProject || !currentExtraction) return;
    clearError(detailError);
    proveButton.disabled = true;
    proveButton.textContent = "Recomputing…";
    try {
      const report = await getJson(
        `/api/qc/projects/${encodeURIComponent(currentProject)}` +
          `/extractions/${encodeURIComponent(currentExtraction)}/prove`,
        { method: "POST" }
      );
      renderProof(report);
    } catch (error) {
      showError(detailError, error.message);
    } finally {
      proveButton.disabled = false;
      proveButton.textContent = "Recompute from the stored samples";
    }
  });

  function renderProof(report) {
    proveHeadline.dataset.proven = String(report.proven);
    if (report.proven) {
      proveHeadline.textContent =
        `Observed. Recomputing from the stored samples reached ` +
        `${report.recomputed_verdict}, the same verdict the record claims` +
        `${report.sql_verdict ? `, and ClickHouse independently reached ${report.sql_verdict}` : ""}.`;
    } else if (report.recomputed_verdict) {
      proveHeadline.textContent =
        `Not supported. The record claims ${report.claimed_verdict}, but its own ` +
        `samples recompute to ${report.recomputed_verdict}.`;
    } else {
      proveHeadline.textContent =
        "Nothing was proven; the run did not reach a recomputation.";
    }

    clear(proveStages);
    report.stages.forEach((stage) => {
      const li = document.createElement("li");
      const name = document.createElement("span");
      name.className = "stage-name";
      name.textContent = stage.stage;
      li.appendChild(name);
      const outcome = document.createElement("span");
      outcome.className = "stage-outcome";
      outcome.dataset.outcome = stage.outcome;
      outcome.textContent = stage.outcome.replace(/_/g, " ");
      li.appendChild(outcome);
      const detail = document.createElement("div");
      detail.className = "muted";
      detail.textContent = stage.detail;
      li.appendChild(detail);
      proveStages.appendChild(li);
    });

    proveResult.hidden = false;
  }
})();
