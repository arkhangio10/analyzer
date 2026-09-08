/* The exported agent's page: read the skill, show it, claim nothing more. */

const labels = {
  es: {
    kicker: "APRENDIZ / AGENTE EXPORTADO",
    meta: "Versión v{version} · destino {destination} · {steps} pasos · exportado {date}",
    steps: "PROCEDIMIENTO",
    can: "QUÉ PUEDE HACER EN EL DESTINO",
    canText: "{actionable} de {total} pasos podrían ejecutarse en este destino. {blocked} están bloqueados.",
    canNone: "No hay plan de adaptación en este paquete.",
    missing: "Falta:",
    guarantees: "GARANTÍAS",
    lineage: "DE DÓNDE SALIÓ",
    details: "REGLAS, EXCEPCIONES E INCERTIDUMBRES",
    rules: "Reglas", exceptions: "Excepciones", uncertainties: "Incertidumbres",
    source: "Fuente", model: "Modelo", tokens: "Tokens", reviewed: "Aprobado", notes: "Notas de revisión",
    none: "Ninguna declarada.",
    guarantee: {
      approved_for_execution: "Conoce el procedimiento; nadie lo ha autorizado a ejecutarlo.",
      physically_measured: "Los ángulos son estimaciones de un modelo de visión, no sensores.",
      hardware_execution_approved: "El hardware queda detrás de un adaptador aparte con aprobación de seguridad.",
      model_weights_updated: "Aprender aquí es adquirir memoria procedural; ningún peso cambió.",
      uploads_included: "Tus videos no están en el paquete.",
      secrets_included: "Ninguna credencial está en el paquete ni en la imagen.",
      provider_calls_at_runtime: "Servir lo aprendido no cuesta nada.",
    },
    errors: { notAgent: "Este servicio no está ejecutándose como agente exportado.", load: "No se pudo cargar el skill: {detail}" },
  },
  en: {
    kicker: "APRENDIZ / EXPORTED AGENT",
    meta: "Version v{version} · destination {destination} · {steps} steps · exported {date}",
    steps: "PROCEDURE",
    can: "WHAT IT CAN DO AT THE DESTINATION",
    canText: "{actionable} of {total} steps could run at this destination. {blocked} are blocked.",
    canNone: "This package carries no adaptation plan.",
    missing: "Missing:",
    guarantees: "GUARANTEES",
    lineage: "WHERE IT CAME FROM",
    details: "RULES, EXCEPTIONS AND UNCERTAINTIES",
    rules: "Rules", exceptions: "Exceptions", uncertainties: "Uncertainties",
    source: "Source", model: "Model", tokens: "Tokens", reviewed: "Approved", notes: "Review notes",
    none: "None stated.",
    guarantee: {
      approved_for_execution: "It knows the procedure; nobody has authorised it to run it.",
      physically_measured: "Angles are a vision model's estimates, not sensors.",
      hardware_execution_approved: "Hardware stays behind a separate, safety-approved adapter.",
      model_weights_updated: "Learning here is procedural-memory acquisition; no weights changed.",
      uploads_included: "Your videos are not in the package.",
      secrets_included: "No credential is in the package or the image.",
      provider_calls_at_runtime: "Serving what was learned costs nothing.",
    },
    errors: { notAgent: "This service is not running as an exported agent.", load: "The skill could not be loaded: {detail}" },
  },
};

function text(selector, value) {
  const node = document.querySelector(selector);
  if (node) node.textContent = value;
}

function fill(list, values, none) {
  const node = document.querySelector(list);
  node.replaceChildren();
  (values?.length ? values : [none]).forEach((value) => {
    const item = document.createElement("li");
    item.textContent = value;
    node.append(item);
  });
}

function render(skill) {
  const t = labels[skill.language] || labels.es;
  document.documentElement.lang = skill.language;
  const procedure = skill.skill.procedure;

  text("#agent-kicker", t.kicker);
  text("#agent-name", skill.skill.name);
  text("#agent-objective", procedure.objective);
  text("#agent-meta", t.meta
    .replace("{version}", String(skill.procedure_version))
    .replace("{destination}", skill.destination)
    .replace("{steps}", String(procedure.steps.length))
    .replace("{date}", new Date(skill.exported_at).toLocaleDateString(skill.language)));
  text("#steps-label", t.steps);
  text("#can-label", t.can);
  text("#guarantees-label", t.guarantees);
  text("#lineage-label", t.lineage);
  text("#details-label", t.details);
  text("#rules-label", t.rules);
  text("#exceptions-label", t.exceptions);
  text("#uncertainties-label", t.uncertainties);

  const steps = document.querySelector("#agent-steps");
  steps.replaceChildren();
  procedure.steps.forEach((step) => {
    const item = document.createElement("li");
    const stamps = (step.source_timestamps || []).join(" · ");
    if (stamps) { const time = document.createElement("time"); time.textContent = stamps; item.append(time); }
    const action = document.createElement("b"); action.textContent = step.action; item.append(action);
    if (step.evidence) { const small = document.createElement("small"); small.textContent = step.evidence; item.append(small); }
    steps.append(item);
  });

  const plan = skill.adaptation;
  text("#agent-can", plan
    ? t.canText
        .replace("{actionable}", String(plan.actionable_step_count))
        .replace("{total}", String(procedure.steps.length))
        .replace("{blocked}", String(plan.blocked_step_count))
    : t.canNone);
  const missing = document.querySelector("#agent-missing");
  missing.replaceChildren();
  (plan?.missing_evidence || []).forEach((item, index) => {
    const li = document.createElement("li");
    li.textContent = (index === 0 ? `${t.missing} ` : "") + item;
    missing.append(li);
  });

  const guarantees = document.querySelector("#agent-guarantees");
  guarantees.replaceChildren();
  Object.entries(skill.guarantees).forEach(([key, value]) => {
    const li = document.createElement("li");
    const code = document.createElement("code"); code.textContent = `${key}: ${value}`;
    const span = document.createElement("span"); span.textContent = t.guarantee[key] || "";
    li.append(code, span);
    guarantees.append(li);
  });

  const lineage = document.querySelector("#agent-lineage");
  lineage.replaceChildren();
  const rows = [
    [t.source, skill.lineage.source_url],
    [t.model, [skill.lineage.requested_model, skill.lineage.model_version].filter(Boolean).join(" · ") || "—"],
    [t.tokens, String(skill.lineage.usage?.total_tokens ?? "—")],
    [t.reviewed, skill.lineage.reviewed_at ? new Date(skill.lineage.reviewed_at).toLocaleString(skill.language) : "—"],
    [t.notes, skill.lineage.review_notes || "—"],
  ];
  rows.forEach(([k, v]) => {
    const dt = document.createElement("dt"); dt.textContent = k;
    const dd = document.createElement("dd"); dd.textContent = v;
    lineage.append(dt, dd);
  });

  fill("#agent-rules", procedure.rules, t.none);
  fill("#agent-exceptions", procedure.exceptions, t.none);
  fill("#agent-uncertainties", procedure.uncertainties, t.none);

  document.querySelector("#agent-grid").hidden = false;
}

async function boot() {
  const lang = navigator.language.toLowerCase().startsWith("es") ? "es" : "en";
  const t = labels[lang];
  try {
    const status = await fetch("/api/agent").then((r) => r.json());
    if (!status.agent_mode) { text("#agent-name", "APRENDIZ"); text("#agent-error", t.errors.notAgent); return; }
    const response = await fetch("/api/skill");
    const body = await response.json();
    if (!response.ok) { text("#agent-name", "APRENDIZ"); text("#agent-error", t.errors.load.replace("{detail}", body.detail || response.status)); return; }
    render(body);
  } catch (error) {
    text("#agent-name", "APRENDIZ");
    text("#agent-error", t.errors.load.replace("{detail}", error?.message || ""));
  }
}

boot();
