const translations = {
  es: {
    pageTitle: "APRENDIZ — Enseña. Valida. Ejecuta.", metaDescription: "Enseña una tarea una vez. Obtén un agente capaz de ejecutarla.",
    socialTitle: "APRENDIZ — Enséñalo una vez. Ejecútalo siempre.", socialDescription: "De demostración a agente validado.",
    skip: "Ir al contenido", brandLabel: "APRENDIZ, inicio", languageLabel: "Seleccionar idioma", navigationLabel: "Navegación principal",
    navMethod: "Método", navProcess: "Proceso", navTrain: "Entrenar", navCreate: "Crear agente <span aria-hidden=\"true\">↗</span>",
    heroEyebrow: "<span class=\"live-dot\" aria-hidden=\"true\"></span> Aprendizaje procedural", heroTitle: "Enséñalo<br><span>una vez.</span>",
    heroSummary: "Convierte demostraciones reales en agentes que entienden el proceso, practican y demuestran lo aprendido.",
    heroAction: "Entrenar un agente <span aria-hidden=\"true\">↗</span>", flowLabel: "Flujo de aprendizaje de APRENDIZ",
    observe: "01 / OBSERVAR", video: "VIDEO", observeCopy: "La demostración se convierte en conocimiento estructurado.",
    validation: "VALIDACIÓN", validationCopy: "Precisión en casos no vistos", delivery: "ENTREGA", deliveryCopy: "Tu agente listo para ejecutar.",
    methodEyebrow: "DEL EJEMPLO A LA EJECUCIÓN", methodTitle: "No memoriza.<br><span>Aprende el proceso.</span>",
    methodCards: [["Observa", "Comprende una demostración en video y extrae pasos, reglas y excepciones."], ["Practica", "Ensaya variaciones progresivas y corrige su memoria procedural."], ["Demuestra", "Se valida con casos protegidos que nunca vio durante el aprendizaje."], ["Ejecuta", "Recibes un agente portable, versionado y listo para correr."]],
    processingEyebrow: "PROCESAMIENTO VISIBLE", processingTitle: "Mira cómo<br><span>aprende.</span>",
    processingIntro: "Cada paso deja evidencia. El sistema muestra qué observa, qué extrae, cómo practica y con qué resultados se valida.",
    demoButton: "Ejecutar simulación local <span aria-hidden=\"true\">↓</span>", demoButtonRunning: "Procesando…", demoButtonAgain: "Repetir simulación <span aria-hidden=\"true\">↻</span>",
    consoleTitle: "APRENDIZ / SESIÓN DE ENTRENAMIENTO", demoBadge: "BACKEND / SIMULACIÓN LOCAL", progressLabel: "Progreso del procesamiento",
    idleStatus: "Listo para iniciar", readyStatus: "Simulación completada", sourceTag: "FUENTE / TRAYECTORIA", demoTask: "Recoger y colocar una pieza frágil",
    sourceDetected: "<i></i> Trayectoria estructurada", pipelineLabel: "Etapas del procesamiento", memory: "MEMORIA PROCEDURAL",
    metricLabels: ["Pasos", "Reglas", "Ejemplos", "Precisión"], logLabel: "Registro de actividad", idleLog: "Esperando una demostración para comenzar…",
    resultTitle: "Procedimiento local validado", resultCopy: "El backend extrajo y evaluó una trayectoria segura en simulación.",
    disclosure: "<span aria-hidden=\"true\">i</span> Esta sesión consulta el backend real y procesa una trayectoria local estructurada. No llama a Gemini, no interpreta todavía el video y no controla hardware.",
    pending: "PENDIENTE", active: "ACTIVO", complete: "LISTO",
    processStages: [["Validando la demostración", "Comprobando articulaciones, tiempo y velocidad"], ["Extrayendo el movimiento", "Convirtiendo waypoints en pasos y reglas"], ["Preparando una repetición", "Construyendo una ejecución contra la referencia"], ["Evaluando la repetición", "Comparando posición, duración y seguridad"], ["Preparando la entrega", "Verificando el contrato del paquete Docker"]],
    processStatuses: ["Validando trayectoria simulada", "Construyendo memoria procedural", "Preparando repetición de referencia", "Evaluando métricas observables", "Preparando contrato Docker"],
    processLogs: ["Sesión creada; validando una trayectoria de seis articulaciones.", "Límites, tiempos y velocidades comprobados por el backend.", "Procedimiento observable extraído desde waypoints estructurados.", "Repetición comparada con la referencia; no es validación de hardware.", "Contrato Docker preparado; llamadas cloud realizadas: 0."],
    processError: "El backend no pudo completar la sesión. Revisa el estado y vuelve a intentarlo.",
    trainerEyebrow: "NUEVO ENTRENAMIENTO", trainerTitle: "¿Qué debe aprender<br>tu agente?", trainerIntro: "Define la tarea, comparte una demostración y revisa el plan antes de iniciar.",
    formProgressLabel: "Progreso de configuración", formMarkers: ["Tarea", "Fuente", "Revisar"], taskLegend: "Describe el resultado que necesitas", taskLabel: "Tarea del agente",
    taskPlaceholder: "Ej.: Enseñar a un brazo robótico a recoger y colocar una pieza frágil.", taskHelp: "Describe el resultado y los límites importantes. Esta primera sesión se ejecutará únicamente en simulación.",
    continue: "Continuar <span aria-hidden=\"true\">→</span>", sourceLegend: "Añade una referencia para la futura demostración", sourceTypeLabel: "Tipo de fuente",
    youtubeCopy: "Referencia a un video instructivo", upload: "Video local", uploadCopy: "El archivo no se envía todavía", videoUrlLabel: "Enlace de referencia",
    selectVideo: "Selecciona un video", fileTypes: "MP4, MOV o WEBM", back: "← Atrás", review: "Revisar <span aria-hidden=\"true\">→</span>",
    reviewLegend: "Todo listo para preparar el aprendizaje", reviewLabels: ["Tarea", "Fuente", "Entrega"], dockerDelivery: "Agente versionado en Docker",
    honesty: "<b>Primera versión funcional.</b> Esta ejecución usa el backend local y una trayectoria robótica estructurada. El enlace o archivo se conserva como referencia, pero el análisis del video con Gemini permanece desactivado.",
    edit: "← Editar", viewProcessing: "Ver procesamiento <span aria-hidden=\"true\">→</span>",
    privacy: "<span aria-hidden=\"true\">●</span> Tus datos y credenciales nunca se incluyen en la imagen Docker.", footer: "ENSEÑA · VALIDA · EJECUTA",
    taskError: "Describe la tarea con al menos 12 caracteres.", urlError: "Añade un enlace de video válido.", fileError: "Selecciona un archivo de video.", noSource: "Sin fuente",
    systemChecking: "Comprobando sistema", systemOnline: "Sistema disponible", systemPreview: "Vista de interfaz",
  },
  en: {
    pageTitle: "APRENDIZ — Teach. Validate. Run.", metaDescription: "Teach a task once. Get an agent capable of running it.",
    socialTitle: "APRENDIZ — Teach it once. Run it always.", socialDescription: "From demonstration to validated agent.",
    skip: "Skip to content", brandLabel: "APRENDIZ, home", languageLabel: "Select language", navigationLabel: "Main navigation",
    navMethod: "Method", navProcess: "Process", navTrain: "Train", navCreate: "Create agent <span aria-hidden=\"true\">↗</span>",
    heroEyebrow: "<span class=\"live-dot\" aria-hidden=\"true\"></span> Procedural learning", heroTitle: "Teach it<br><span>once.</span>",
    heroSummary: "Turn real demonstrations into agents that understand the process, practice it, and prove what they learned.",
    heroAction: "Train an agent <span aria-hidden=\"true\">↗</span>", flowLabel: "APRENDIZ learning flow",
    observe: "01 / OBSERVE", video: "VIDEO", observeCopy: "The demonstration becomes structured knowledge.", validation: "VALIDATION", validationCopy: "Accuracy on unseen cases",
    delivery: "DELIVERY", deliveryCopy: "Your agent, ready to run.", methodEyebrow: "FROM EXAMPLE TO EXECUTION", methodTitle: "It does not memorize.<br><span>It learns the process.</span>",
    methodCards: [["Observe", "Understand a video demonstration and extract steps, rules, and exceptions."], ["Practice", "Try progressive variations and correct its procedural memory."], ["Prove", "Validate against protected cases it never saw while learning."], ["Execute", "Receive a portable, versioned agent that is ready to run."]],
    processingEyebrow: "VISIBLE PROCESSING", processingTitle: "Watch it<br><span>learn.</span>",
    processingIntro: "Every step leaves evidence. See what the system observes, what it extracts, how it practices, and how results are validated.",
    demoButton: "Run local simulation <span aria-hidden=\"true\">↓</span>", demoButtonRunning: "Processing…", demoButtonAgain: "Run simulation again <span aria-hidden=\"true\">↻</span>",
    consoleTitle: "APRENDIZ / TRAINING SESSION", demoBadge: "BACKEND / LOCAL SIMULATION", progressLabel: "Processing progress", idleStatus: "Ready to start",
    readyStatus: "Simulation complete", sourceTag: "SOURCE / TRAJECTORY", demoTask: "Pick and place a fragile component", sourceDetected: "<i></i> Structured trajectory",
    pipelineLabel: "Processing stages", memory: "PROCEDURAL MEMORY", metricLabels: ["Steps", "Rules", "Examples", "Accuracy"], logLabel: "Activity log",
    idleLog: "Waiting for a demonstration to begin…", resultTitle: "Local procedure validated", resultCopy: "The backend extracted and evaluated a safe simulated trajectory.",
    disclosure: "<span aria-hidden=\"true\">i</span> This session calls the real backend and processes a structured local trajectory. It does not call Gemini, interpret the video yet, or control hardware.",
    pending: "PENDING", active: "ACTIVE", complete: "DONE",
    processStages: [["Validating the demonstration", "Checking joints, timing, and velocity"], ["Extracting the motion", "Turning waypoints into steps and rules"], ["Preparing a replay", "Building an execution against the reference"], ["Evaluating the replay", "Comparing position, duration, and safety"], ["Preparing delivery", "Checking the Docker package contract"]],
    processStatuses: ["Validating simulated trajectory", "Building procedural memory", "Preparing reference replay", "Evaluating observable metrics", "Preparing Docker contract"],
    processLogs: ["Session created; validating a six-joint trajectory.", "Limits, timestamps, and velocities checked by the backend.", "Observable procedure extracted from structured waypoints.", "Replay compared with its reference; this is not hardware validation.", "Docker contract prepared; cloud calls made: 0."],
    processError: "The backend could not complete the session. Check its status and try again.",
    trainerEyebrow: "NEW TRAINING", trainerTitle: "What should your<br>agent learn?", trainerIntro: "Define the task, share a demonstration, and review the plan before starting.",
    formProgressLabel: "Configuration progress", formMarkers: ["Task", "Source", "Review"], taskLegend: "Describe the result you need", taskLabel: "Agent task",
    taskPlaceholder: "Example: Teach a robot arm to pick and place a fragile component.", taskHelp: "Describe the outcome and important limits. This first session runs in simulation only.",
    continue: "Continue <span aria-hidden=\"true\">→</span>", sourceLegend: "Add a reference for the future demonstration", sourceTypeLabel: "Source type", youtubeCopy: "Instructional video reference",
    upload: "Local video", uploadCopy: "The file is not uploaded yet", videoUrlLabel: "Reference link", selectVideo: "Select a video", fileTypes: "MP4, MOV, or WEBM",
    back: "← Back", review: "Review <span aria-hidden=\"true\">→</span>", reviewLegend: "Everything is ready to prepare learning",
    reviewLabels: ["Task", "Source", "Delivery"], dockerDelivery: "Versioned agent in Docker",
    honesty: "<b>First functional version.</b> This run uses the local backend and a structured robot trajectory. The link or file is retained as a reference, but Gemini video analysis remains disabled.",
    edit: "← Edit", viewProcessing: "View processing <span aria-hidden=\"true\">→</span>",
    privacy: "<span aria-hidden=\"true\">●</span> Your data and credentials are never included in the Docker image.", footer: "TEACH · VALIDATE · EXECUTE",
    taskError: "Describe the task using at least 12 characters.", urlError: "Add a valid video link.", fileError: "Select a video file.", noSource: "No source",
    systemChecking: "Checking system", systemOnline: "System available", systemPreview: "Interface preview",
  },
};

const form = document.querySelector("#trainer-form");
const steps = [...document.querySelectorAll(".form-step")];
const markers = [...document.querySelectorAll("[data-step-marker]")];
const taskInput = document.querySelector("#task-description");
const videoUrl = document.querySelector("#video-url");
const videoFile = document.querySelector("#video-file");
const taskError = document.querySelector("#task-error");
const sourceError = document.querySelector("#source-error");
const processingConsole = document.querySelector("#processing-console");
const processResult = document.querySelector("#process-result");
const processLog = document.querySelector("#process-log");
const processButton = document.querySelector("#demo-processing");
const processSubmit = form.querySelector("button[type='submit']");
const processStages = [...document.querySelectorAll("[data-process-stage]")];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
let currentStep = 1;
let currentLanguage = "es";
let systemOnline = false;
let systemChecked = false;
let processStage = -1;
let processPollTimer = null;
let currentProcessTask = "";
let currentProcessSource = "";
let processStatus = "idle";
let processProgress = 0;
let processCompletedStages = 0;
let processSession = null;
let processErrorMessage = "";

function setContent(selector, value, useHtml = false) {
  const element = document.querySelector(selector);
  if (!element) return;
  if (useHtml) element.innerHTML = value;
  else element.textContent = value;
}

function applyLanguage(language) {
  currentLanguage = translations[language] ? language : "es";
  const t = translations[currentLanguage];
  document.documentElement.lang = currentLanguage;
  document.title = t.pageTitle;
  document.querySelector('meta[name="description"]').content = t.metaDescription;
  document.querySelector('meta[property="og:title"]').content = t.socialTitle;
  document.querySelector('meta[property="og:description"]').content = t.socialDescription;
  document.querySelector('meta[name="twitter:title"]').content = t.socialTitle;
  document.querySelector('meta[name="twitter:description"]').content = t.socialDescription;
  setContent(".skip-link", t.skip);
  document.querySelector(".brand").ariaLabel = t.brandLabel;
  document.querySelector(".language-switch").ariaLabel = t.languageLabel;
  document.querySelector("nav").ariaLabel = t.navigationLabel;
  setContent('nav a[href="#metodo"]', t.navMethod);
  setContent('nav a[href="#procesamiento"]', t.navProcess);
  setContent('nav a[href="#entrenar"]:not(.nav-cta)', t.navTrain);
  setContent(".nav-cta", t.navCreate, true);
  setContent(".hero-copy .eyebrow", t.heroEyebrow, true);
  setContent("#hero-title", t.heroTitle, true);
  setContent(".hero-summary", t.heroSummary);
  setContent(".primary-action", t.heroAction, true);
  document.querySelector(".hero-stage").ariaLabel = t.flowLabel;
  setContent(".card-topline span:first-child", t.observe);
  setContent(".card-topline span:last-child", t.video);
  setContent(".flow-card-main > p", t.observeCopy);
  setContent(".flow-card-score .card-label", t.validation);
  setContent(".flow-card-score p", t.validationCopy);
  setContent(".flow-card-export .card-label", t.delivery);
  setContent(".flow-card-export p", t.deliveryCopy);
  setContent(".method .eyebrow", t.methodEyebrow);
  setContent("#method-title", t.methodTitle, true);
  document.querySelectorAll(".method-grid article").forEach((card, index) => { card.querySelector("h3").textContent = t.methodCards[index][0]; card.querySelector("p").textContent = t.methodCards[index][1]; });
  setContent(".processing-heading .eyebrow", t.processingEyebrow);
  setContent("#processing-title", t.processingTitle, true);
  setContent(".processing-intro p", t.processingIntro);
  setContent(".console-title b", t.consoleTitle);
  setContent(".demo-badge", t.demoBadge);
  document.querySelector(".process-progress").ariaLabel = t.progressLabel;
  setContent(".monitor-tag", t.sourceTag);
  setContent(".signal-row span:first-child", t.sourceDetected, true);
  document.querySelector(".pipeline-list").ariaLabel = t.pipelineLabel;
  setContent(".panel-label span:first-child", t.memory);
  document.querySelectorAll(".extraction-metrics article > span").forEach((label, index) => { label.textContent = t.metricLabels[index]; });
  processLog.ariaLabel = t.logLabel;
  setContent(".process-result b", t.resultTitle);
  setContent(".process-result small", t.resultCopy);
  setContent(".demo-disclosure", t.disclosure, true);
  setContent(".trainer-intro .eyebrow", t.trainerEyebrow);
  setContent("#trainer-title", t.trainerTitle, true);
  setContent(".trainer-intro > p:last-child", t.trainerIntro);
  document.querySelector(".step-nav").ariaLabel = t.formProgressLabel;
  markers.forEach((marker, index) => { marker.innerHTML = `<span>0${index + 1}</span> ${t.formMarkers[index]}`; });
  setContent('[data-step="1"] legend', t.taskLegend);
  setContent('label[for="task-description"]', t.taskLabel);
  taskInput.placeholder = t.taskPlaceholder;
  setContent(".field-help", t.taskHelp);
  setContent('[data-step="1"] [data-next]', t.continue, true);
  setContent('[data-step="2"] legend', t.sourceLegend);
  document.querySelector(".source-options").ariaLabel = t.sourceTypeLabel;
  setContent('.source-option:first-child small', t.youtubeCopy);
  setContent('.source-option:last-child b', t.upload);
  setContent('.source-option:last-child small', t.uploadCopy);
  setContent('label[for="video-url"]', t.videoUrlLabel);
  if (!videoFile.files.length) setContent("#file-label", t.selectVideo);
  setContent(".file-drop small", t.fileTypes);
  setContent('[data-step="2"] [data-back]', t.back);
  setContent('[data-step="2"] [data-next]', t.review, true);
  setContent('[data-step="3"] legend', t.reviewLegend);
  document.querySelectorAll(".review-list dt").forEach((label, index) => { label.textContent = t.reviewLabels[index]; });
  setContent(".review-list div:last-child dd", t.dockerDelivery);
  setContent(".honesty-note p", t.honesty, true);
  setContent('[data-step="3"] [data-back]', t.edit);
  setContent('[data-step="3"] button[type="submit"]', t.viewProcessing, true);
  setContent(".privacy-note", t.privacy, true);
  setContent("footer span:last-child", t.footer);
  document.querySelectorAll("[data-language]").forEach((button) => { button.setAttribute("aria-pressed", String(button.dataset.language === currentLanguage)); });
  try { localStorage.setItem("aprendiz-language", currentLanguage); } catch (_) { /* Keep preference in memory. */ }
  updateSystemStatus();
  renderProcessState();
}

function showStep(stepNumber) {
  currentStep = stepNumber;
  steps.forEach((step) => { const active = Number(step.dataset.step) === stepNumber; step.hidden = !active; step.classList.toggle("is-active", active); });
  markers.forEach((marker) => { const markerStep = Number(marker.dataset.stepMarker); marker.classList.toggle("is-active", markerStep === stepNumber); marker.classList.toggle("is-complete", markerStep < stepNumber); });
  steps.find((step) => Number(step.dataset.step) === stepNumber)?.querySelector("textarea, input:not([type='radio']), button")?.focus({ preventScroll: true });
}

function selectedSourceType() { return form.elements["source-type"].value; }

function validateCurrentStep() {
  const t = translations[currentLanguage];
  if (currentStep === 1) {
    const valid = taskInput.value.trim().length >= 12;
    taskError.textContent = valid ? "" : t.taskError;
    taskInput.setAttribute("aria-invalid", String(!valid));
    return valid;
  }
  if (currentStep === 2) {
    const type = selectedSourceType();
    const valid = Boolean((type === "youtube" && videoUrl.value.trim() && videoUrl.checkValidity()) || (type === "upload" && videoFile.files.length > 0));
    sourceError.textContent = valid ? "" : type === "youtube" ? t.urlError : t.fileError;
    return valid;
  }
  return true;
}

function fillReview() {
  const source = selectedSourceType() === "youtube" ? videoUrl.value.trim() : videoFile.files[0]?.name;
  setContent("#review-task", taskInput.value.trim());
  setContent("#review-source", source || translations[currentLanguage].noSource);
}

function renderProcessMetrics() {
  const training = processSession?.training_result;
  const evaluation = processSession?.evaluation_result;
  const values = training && evaluation
    ? [
        String(training.procedure?.steps?.length || 0),
        String(training.procedure?.rules?.length || 0),
        String(training.procedure?.examples?.length || 0),
        `${Math.round(evaluation.score * 100)}%`,
      ]
    : ["…", "…", "—", "—"];
  ["#metric-steps", "#metric-rules", "#metric-examples", "#metric-score"].forEach((selector, index) => setContent(selector, values[index]));
}

function renderProcessLogs(isIdle, isComplete) {
  const t = translations[currentLanguage];
  if (isIdle) {
    processLog.innerHTML = `<p><time>00</time><span>${processErrorMessage || t.idleLog}</span></p>`;
    return;
  }
  const visibleCount = isComplete
    ? processStages.length
    : Math.min(processStages.length, processCompletedStages + 1);
  processLog.innerHTML = "";
  for (let index = 0; index < visibleCount; index += 1) {
    const line = document.createElement("p");
    line.innerHTML = `<time>${String(index + 1).padStart(2, "0")}</time><span></span>`;
    line.querySelector("span").textContent = t.processLogs[index];
    processLog.append(line);
  }
}

function renderProcessState() {
  const t = translations[currentLanguage];
  const isIdle = processStatus === "idle" || processStatus === "failed";
  const isComplete = processStatus === "completed";
  const progress = isIdle ? 0 : processProgress;
  setContent("#process-status", processStatus === "failed" ? t.processError : isIdle ? t.idleStatus : isComplete ? t.readyStatus : t.processStatuses[processStage]);
  setContent("#process-percent", `${progress}%`);
  document.querySelector("#process-progress-bar").style.width = `${progress}%`;
  document.querySelector(".process-progress").setAttribute("aria-valuenow", String(progress));
  setContent("#monitor-task", currentProcessTask || t.demoTask);
  setContent("#source-name", currentProcessSource || "local-simulation://guided-demo");
  setContent("#monitor-time", isIdle ? "00/05" : `${String(isComplete ? 5 : processCompletedStages).padStart(2, "0")}/05`);
  setContent("#memory-version", processCompletedStages >= 2 || isComplete ? "V1" : "V0");
  processStages.forEach((item, index) => {
    item.querySelector("b").textContent = t.processStages[index][0];
    item.querySelector("small").textContent = t.processStages[index][1];
    const complete = isComplete || index < processCompletedStages;
    const active = !isIdle && !isComplete && index === processStage;
    item.classList.toggle("is-complete", complete);
    item.classList.toggle("is-active", active);
    item.querySelector(".stage-state").textContent = complete ? t.complete : active ? t.active : t.pending;
  });
  renderProcessMetrics();
  renderProcessLogs(isIdle, isComplete);
  processResult.classList.toggle("is-ready", isComplete);
  processingConsole.classList.toggle("is-running", !isIdle && !isComplete);
  processButton.disabled = processStatus === "processing";
  processSubmit.disabled = processStatus === "processing";
  setContent("#demo-processing", !isIdle && !isComplete ? t.demoButtonRunning : isComplete ? t.demoButtonAgain : t.demoButton, true);
}

function applyProcessingSession(session) {
  processSession = session;
  processStatus = session.status;
  processProgress = session.progress_percent;
  processCompletedStages = session.completed_stage_count;
  processStage = session.current_stage_index ?? processStages.length;
  processErrorMessage = "";
  renderProcessState();
}

async function pollProcessingSession(sessionId) {
  try {
    const response = await fetch(`/api/processing/robot-motion/${encodeURIComponent(sessionId)}`);
    if (!response.ok) throw new Error(`Processing status failed: ${response.status}`);
    const session = await response.json();
    applyProcessingSession(session);
    if (session.status === "processing") {
      processPollTimer = window.setTimeout(() => pollProcessingSession(sessionId), reducedMotion.matches ? 750 : 500);
    }
  } catch (error) {
    processStatus = "failed";
    processErrorMessage = translations[currentLanguage].processError;
    renderProcessState();
    console.error(error);
  }
}

async function startProcessing(task, source, immediate = false) {
  clearTimeout(processPollTimer);
  currentProcessTask = task || translations[currentLanguage].demoTask;
  currentProcessSource = source || "local-simulation://guided-demo";
  processStatus = "processing";
  processProgress = 0;
  processCompletedStages = 0;
  processStage = 0;
  processSession = null;
  processErrorMessage = "";
  renderProcessState();
  const processingSection = document.querySelector("#procesamiento");
  if (immediate) {
    const previousScrollBehavior = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = "auto";
    processingSection.scrollIntoView({ block: "start" });
    requestAnimationFrame(() => { document.documentElement.style.scrollBehavior = previousScrollBehavior; });
  } else {
    processingSection.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "start" });
  }
  try {
    const response = await fetch("/api/processing/robot-motion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task_name: currentProcessTask,
        objective: currentProcessTask,
        source: currentProcessSource,
        language: currentLanguage,
        simulation_only: true,
      }),
    });
    if (!response.ok) throw new Error(`Processing start failed: ${response.status}`);
    const session = await response.json();
    applyProcessingSession(session);
    if (session.status === "processing") pollProcessingSession(session.session_id);
  } catch (error) {
    processStatus = "failed";
    processErrorMessage = translations[currentLanguage].processError;
    renderProcessState();
    console.error(error);
  }
}

form.addEventListener("click", (event) => {
  const nextButton = event.target.closest("[data-next]");
  const backButton = event.target.closest("[data-back]");
  if (nextButton && validateCurrentStep()) { if (currentStep === 2) fillReview(); showStep(Math.min(3, currentStep + 1)); }
  if (backButton) showStep(Math.max(1, currentStep - 1));
});

document.querySelectorAll("input[name='source-type']").forEach((radio) => {
  radio.addEventListener("change", () => {
    document.querySelectorAll(".source-option").forEach((option) => option.classList.toggle("is-selected", option.contains(radio)));
    document.querySelectorAll("[data-source-panel]").forEach((panel) => { panel.hidden = panel.dataset.sourcePanel !== radio.value; });
    sourceError.textContent = "";
  });
});

videoFile.addEventListener("change", () => setContent("#file-label", videoFile.files[0]?.name || translations[currentLanguage].selectVideo));
form.addEventListener("submit", (event) => { event.preventDefault(); const source = selectedSourceType() === "youtube" ? videoUrl.value.trim() : videoFile.files[0]?.name; startProcessing(taskInput.value.trim(), source); });
processButton.addEventListener("click", () => startProcessing(translations[currentLanguage].demoTask, "local-simulation://guided-demo"));
document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.language)));

const stage = document.querySelector(".hero-stage");
stage.addEventListener("pointermove", (event) => {
  if (reducedMotion.matches) return;
  const bounds = stage.getBoundingClientRect();
  const x = (event.clientX - bounds.left) / bounds.width - 0.5;
  const y = (event.clientY - bounds.top) / bounds.height - 0.5;
  stage.style.setProperty("--card-x", `${x * 14}px`); stage.style.setProperty("--card-y", `${y * 10}px`);
  stage.style.setProperty("--score-x", `${x * -18}px`); stage.style.setProperty("--score-y", `${y * -12}px`);
  stage.style.setProperty("--export-x", `${x * 22}px`); stage.style.setProperty("--export-y", `${y * 14}px`);
});
stage.addEventListener("pointerleave", () => ["--card-x", "--card-y", "--score-x", "--score-y", "--export-x", "--export-y"].forEach((property) => stage.style.removeProperty(property)));

function updateSystemStatus() {
  const t = translations[currentLanguage];
  setContent("#system-status", !systemChecked ? t.systemChecking : systemOnline ? t.systemOnline : t.systemPreview);
  document.querySelector(".system-status").classList.toggle("is-online", systemOnline);
}

const pageParameters = new URLSearchParams(window.location.search);
let preferredLanguage = navigator.language.toLowerCase().startsWith("es") ? "es" : "en";
try { preferredLanguage = localStorage.getItem("aprendiz-language") || preferredLanguage; } catch (_) { /* Use browser language. */ }
if (translations[pageParameters.get("lang")]) preferredLanguage = pageParameters.get("lang");
applyLanguage(preferredLanguage);
fetch("/health").then((response) => { if (!response.ok) throw new Error("Health check failed"); return response.json(); }).then(() => { systemChecked = true; systemOnline = true; updateSystemStatus(); }).catch(() => { systemChecked = true; systemOnline = false; updateSystemStatus(); });
