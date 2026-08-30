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
    formProgressLabel: "Progreso de configuración", formMarkers: ["Tarea", "Destino", "Fuente", "Revisar"], taskLegend: "Describe el resultado que necesitas", taskLabel: "Tarea del agente",
    taskPlaceholder: "Ej.: Enseñar a un brazo robótico a recoger y colocar una pieza frágil.", taskHelp: "Describe el resultado y los límites importantes. Esta primera sesión se ejecutará únicamente en simulación.",
    continue: "Continuar <span aria-hidden=\"true\">→</span>", destinationLegend: "¿Dónde ejecutará lo aprendido?", destinationTypeLabel: "Destino de ejecución",
    robot: "Robot", robotCopy: "Movimiento validado primero en simulación", computer: "Computadora", computerCopy: "Procedimiento aislado antes de ejecutarlo",
    robotModelLabel: "Marca y modelo exacto", robotModelPlaceholder: "Ej.: Unitree Go2", robotHelp: "Usaremos ARP-1 y seleccionaremos el simulador compatible automáticamente.",
    computerAppLabel: "Aplicación objetivo", computerAppPlaceholder: "Ej.: Google Chrome, Excel o Blender", computerHelp: "El sistema operativo se detectará automáticamente y la primera ejecución será aislada.",
    sourceLegend: "Añade una referencia para la futura demostración", sourceTypeLabel: "Tipo de fuente",
    youtubeCopy: "Referencia a un video instructivo", upload: "Video local", uploadCopy: "El archivo no se envía todavía", automatic: "Búsqueda automática", automaticCopy: "Encuentra referencias para que las apruebes", videoUrlLabel: "Enlace de referencia",
    searchLabel: "¿Qué demostración debe buscar?", searchPlaceholder: "Ej.: perro corriendo vista lateral biomecánica", searchButton: "Buscar referencias", searching: "Buscando…", searchHelp: "La búsqueda usa una llamada acotada; ningún video se analiza hasta que lo apruebes.", approveSources: "Aprobar selección", approving: "Aprobando…", sourceApproved: "{count} referencia(s) aprobada(s). El análisis aún no ha comenzado.", searchEmpty: "No se encontraron videos para esta búsqueda.", searchUnavailable: "La búsqueda automática no está configurada todavía. Puedes usar un enlace directo mientras se habilita YouTube Data API.", selectCandidate: "Selecciona al menos una referencia antes de aprobar.",
    selectVideo: "Selecciona un video", fileTypes: "MP4, MOV o WEBM", back: "← Atrás", review: "Revisar <span aria-hidden=\"true\">→</span>",
    reviewLegend: "Todo listo para preparar el aprendizaje", reviewLabels: ["Tarea", "Destino", "Configuración", "Fuente", "Entrega"], dockerDelivery: "Agente versionado en Docker",
    robotReview: "Robot / simulación primero", computerReview: "Computadora / entorno aislado", robotConfig: "ARP-1 · simulador automático", computerConfig: "Sistema operativo automático · sandbox obligatorio",
    honestyRobot: "<b>Primera versión funcional.</b> El contrato del robot se crea en el backend y esta demostración procesa una trayectoria local estructurada. No controla hardware físico.",
    honestyComputer: "<b>Ensayo funcional disponible.</b> El navegador aislado sólo ejecutará las acciones que revises y apruebes para un dominio público exacto. El plan todavía no se extrae automáticamente del video.",
    edit: "← Editar", prepareProject: "Preparar proyecto <span aria-hidden=\"true\">→</span>", projectReadyRobot: "Proyecto {id} creado. Iniciando validación robótica local…", projectReadyComputer: "Proyecto {id} creado. Ya puedes definir y aprobar un ensayo aislado de navegador.", projectError: "No se pudo preparar el proyecto. Revisa los datos e inténtalo nuevamente.",
    privacy: "<span aria-hidden=\"true\">●</span> Tus datos y credenciales nunca se incluyen en la imagen Docker.", footer: "ENSEÑA · VALIDA · EJECUTA",
    taskError: "Describe la tarea con al menos 12 caracteres.", robotModelError: "Indica la marca y el modelo del robot.", computerAppError: "Indica la aplicación donde se ejecutará la tarea.", urlError: "Añade un enlace de video válido.", fileError: "Selecciona un archivo de video.", automaticError: "Busca y aprueba al menos una referencia.", noSource: "Sin fuente",
    systemChecking: "Comprobando sistema", systemOnline: "Sistema disponible", systemPreview: "Vista de interfaz",
    practiceEyebrow: "ENSAYO APROBADO", practiceTitle: "Prueba la tarea en un navegador aislado.", practiceIntro: "Define un destino público y revisa las acciones exactas antes de permitir una conexión externa.",
    practiceDisclosure: "Este plan lo defines y apruebas tú. Todavía no se genera automáticamente desde el video y no usa Gemini.", targetLabel: "Página pública de práctica", targetPlaceholder: "https://example.com", targetHelp: "Sólo se autorizará el dominio exacto de este enlace.",
    selectorLabel: "Campo CSS opcional", selectorPlaceholder: "input[name='display-name']", selectorHelp: "Déjalo vacío si sólo quieres comprobar la navegación.", sampleLabel: "Texto de prueba no sensible", samplePlaceholder: "Dato de ejemplo", sampleHelp: "No uses contraseñas, tokens, credenciales ni datos privados.",
    planLabel: "PLAN A REVISAR", planEmpty: "Indica una página pública para construir el plan.", planNavigate: "Abrir {url}", planType: "Escribir texto de prueba en {selector}", approvalLabel: "Revisé estas acciones y apruebo la conexión externa únicamente a este dominio.", runPractice: "Ejecutar ensayo aprobado <span aria-hidden=\"true\">→</span>",
    practiceProgressLabel: "EVIDENCIA DE EJECUCIÓN", practiceResultLabel: "RESULTADO", practiceStages: [["Preparando plan", "Pendiente"], ["Validando dominio", "Pendiente"], ["Ejecutando Chromium", "Pendiente"], ["Registrando resultado", "Pendiente"]], practiceActive: "Activo", practiceDone: "Listo", practiceWaiting: "Esperando aprobación", practiceRunning: "Ejecutando ensayo…",
    practiceActionsLabel: "Acciones", practiceNetworkLabel: "Solicitudes permitidas", practiceBlockedLabel: "Bloqueadas", practiceCloudLabel: "Llamadas cloud", practiceComplete: "Ensayo completado", practicePartial: "Ensayo parcialmente completado", practiceBlocked: "Ensayo bloqueado", practiceRejected: "Ensayo rechazado", practiceSuccessSummary: "El navegador terminó dentro del dominio aprobado y devolvió evidencia redactada.", practiceFailureSummary: "La política de seguridad o el navegador impidió completar el plan. Revisa la evidencia visible.",
    practiceUrlError: "Indica una URL pública HTTP(S) sin credenciales y usando el puerto estándar.", practicePairError: "Para escribir texto debes completar tanto el selector CSS como el texto de prueba.", practiceApprovalError: "Revisa el plan y marca la aprobación antes de ejecutarlo.", practiceGenericError: "No se pudo ejecutar el ensayo. Revisa el plan y vuelve a intentarlo.",
    videoProcedureEyebrow: "EXTRACCIÓN CONTROLADA", videoProcedureTitle: "Convierte el video aprobado en un procedimiento revisable.", videoProcedureIntro: "Vertex analiza una sola fuente con resolución baja. El resultado no se ejecutará hasta que lo revises.", videoSourceLabel: "FUENTE APROBADA",
    videoCostLabel: "Autorizo una llamada acotada a Vertex y el consumo asociado de créditos.", extractVideo: "Extraer procedimiento <span aria-hidden=\"true\">→</span>", extractingVideo: "Analizando video…", videoCostError: "Confirma la fuente y el uso de créditos antes de iniciar.", videoExtractionError: "No se pudo registrar la extracción.",
    videoStatusLabel: "ESTADO DE EXTRACCIÓN", videoWaiting: "Esperando autorización", videoRunning: "Vertex está analizando la fuente", videoFailed: "Extracción no completada", videoAwaitingReview: "Procedimiento pendiente de revisión", videoApproved: "Procedimiento aprobado", videoRejected: "Procedimiento rechazado", videoFailureSummary: "Vertex no devolvió un procedimiento. Código seguro: {code}.", videoReadySummary: "Revisa la evidencia antes de permitir cualquier adaptación o ejecución.", videoReviewedSummary: "La decisión humana quedó registrada; no se ejecutaron acciones.",
    videoVersionLabel: "Versión", videoTokenLabel: "Tokens", videoTimeLabel: "Tiempo", videoCallLabel: "Llamadas cloud", procedureReviewLabel: "PROCEDIMIENTO A REVISAR", procedureRulesLabel: "Reglas", procedureExceptionsLabel: "Excepciones", procedureExamplesLabel: "Ejemplos", procedureUncertaintiesLabel: "Incertidumbres", procedureNotesLabel: "Notas de revisión opcionales", rejectProcedure: "Rechazar", approveProcedure: "Aprobar procedimiento", reviewingProcedure: "Registrando decisión…", emptyEvidence: "No declarado por la fuente.",
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
    formProgressLabel: "Configuration progress", formMarkers: ["Task", "Destination", "Source", "Review"], taskLegend: "Describe the result you need", taskLabel: "Agent task",
    taskPlaceholder: "Example: Teach a robot arm to pick and place a fragile component.", taskHelp: "Describe the outcome and important limits. This first session runs in simulation only.",
    continue: "Continue <span aria-hidden=\"true\">→</span>", destinationLegend: "Where will the learned behavior run?", destinationTypeLabel: "Execution destination",
    robot: "Robot", robotCopy: "Motion validated in simulation first", computer: "Computer", computerCopy: "Procedure isolated before execution",
    robotModelLabel: "Exact brand and model", robotModelPlaceholder: "Example: Unitree Go2", robotHelp: "We will use ARP-1 and select a compatible simulator automatically.",
    computerAppLabel: "Target application", computerAppPlaceholder: "Example: Google Chrome, Excel, or Blender", computerHelp: "The operating system will be detected automatically and the first run will be isolated.",
    sourceLegend: "Add a reference for the future demonstration", sourceTypeLabel: "Source type", youtubeCopy: "Instructional video reference",
    upload: "Local video", uploadCopy: "The file is not uploaded yet", automatic: "Automatic search", automaticCopy: "Find references for you to approve", videoUrlLabel: "Reference link", selectVideo: "Select a video", fileTypes: "MP4, MOV, or WEBM",
    searchLabel: "What demonstration should it find?", searchPlaceholder: "Example: dog running lateral view biomechanics", searchButton: "Find references", searching: "Searching…", searchHelp: "Search uses one bounded call; no video is analyzed until you approve it.", approveSources: "Approve selection", approving: "Approving…", sourceApproved: "{count} reference(s) approved. Analysis has not started yet.", searchEmpty: "No videos were found for this search.", searchUnavailable: "Automatic search is not configured yet. You can use a direct link while YouTube Data API is enabled.", selectCandidate: "Select at least one reference before approval.",
    back: "← Back", review: "Review <span aria-hidden=\"true\">→</span>", reviewLegend: "Everything is ready to prepare learning",
    reviewLabels: ["Task", "Destination", "Configuration", "Source", "Delivery"], dockerDelivery: "Versioned agent in Docker",
    robotReview: "Robot / simulation first", computerReview: "Computer / isolated environment", robotConfig: "ARP-1 · automatic simulator", computerConfig: "Automatic OS · mandatory sandbox",
    honestyRobot: "<b>First functional version.</b> The robot contract is created by the backend and this demonstration processes a structured local trajectory. It does not control physical hardware.",
    honestyComputer: "<b>Functional rehearsal available.</b> The isolated browser will run only the actions you review and approve for one exact public domain. The plan is not extracted automatically from the video yet.",
    edit: "← Edit", prepareProject: "Prepare project <span aria-hidden=\"true\">→</span>", projectReadyRobot: "Project {id} created. Starting local robot validation…", projectReadyComputer: "Project {id} created. You can now define and approve an isolated browser rehearsal.", projectError: "The project could not be prepared. Check the data and try again.",
    privacy: "<span aria-hidden=\"true\">●</span> Your data and credentials are never included in the Docker image.", footer: "TEACH · VALIDATE · EXECUTE",
    taskError: "Describe the task using at least 12 characters.", robotModelError: "Enter the robot brand and model.", computerAppError: "Enter the application where the task will run.", urlError: "Add a valid video link.", fileError: "Select a video file.", automaticError: "Find and approve at least one reference.", noSource: "No source",
    systemChecking: "Checking system", systemOnline: "System available", systemPreview: "Interface preview",
    practiceEyebrow: "APPROVED REHEARSAL", practiceTitle: "Test the task in an isolated browser.", practiceIntro: "Choose a public destination and review the exact actions before allowing an external connection.",
    practiceDisclosure: "You define and approve this plan. It is not generated automatically from the video yet, and it does not use Gemini.", targetLabel: "Public practice page", targetPlaceholder: "https://example.com", targetHelp: "Only the exact domain from this URL will be approved.",
    selectorLabel: "Optional CSS field", selectorPlaceholder: "input[name='display-name']", selectorHelp: "Leave it empty if you only want to verify navigation.", sampleLabel: "Non-sensitive sample text", samplePlaceholder: "Sample data", sampleHelp: "Do not use passwords, tokens, credentials, or private data.",
    planLabel: "PLAN TO REVIEW", planEmpty: "Enter a public page to build the plan.", planNavigate: "Open {url}", planType: "Type sample text into {selector}", approvalLabel: "I reviewed these actions and approve the external connection only to this domain.", runPractice: "Run approved rehearsal <span aria-hidden=\"true\">→</span>",
    practiceProgressLabel: "EXECUTION EVIDENCE", practiceResultLabel: "RESULT", practiceStages: [["Preparing plan", "Pending"], ["Validating domain", "Pending"], ["Running Chromium", "Pending"], ["Recording result", "Pending"]], practiceActive: "Active", practiceDone: "Done", practiceWaiting: "Waiting for approval", practiceRunning: "Running rehearsal…",
    practiceActionsLabel: "Actions", practiceNetworkLabel: "Allowed requests", practiceBlockedLabel: "Blocked", practiceCloudLabel: "Cloud calls", practiceComplete: "Rehearsal completed", practicePartial: "Rehearsal partially completed", practiceBlocked: "Rehearsal blocked", practiceRejected: "Rehearsal rejected", practiceSuccessSummary: "The browser finished inside the approved domain and returned redacted evidence.", practiceFailureSummary: "The safety policy or browser prevented the plan from completing. Review the visible evidence.",
    practiceUrlError: "Enter a public HTTP(S) URL without credentials and using the standard port.", practicePairError: "To type text, complete both the CSS selector and the sample text.", practiceApprovalError: "Review the plan and check the approval before running it.", practiceGenericError: "The rehearsal could not run. Review the plan and try again.",
    videoProcedureEyebrow: "CONTROLLED EXTRACTION", videoProcedureTitle: "Turn the approved video into a reviewable procedure.", videoProcedureIntro: "Vertex analyzes one source at low resolution. Nothing will execute until you review the result.", videoSourceLabel: "APPROVED SOURCE",
    videoCostLabel: "I authorize one bounded Vertex call and the associated credit usage.", extractVideo: "Extract procedure <span aria-hidden=\"true\">→</span>", extractingVideo: "Analyzing video…", videoCostError: "Confirm the source and credit usage before starting.", videoExtractionError: "The extraction could not be recorded.",
    videoStatusLabel: "EXTRACTION STATUS", videoWaiting: "Waiting for authorization", videoRunning: "Vertex is analyzing the source", videoFailed: "Extraction not completed", videoAwaitingReview: "Procedure awaiting review", videoApproved: "Procedure approved", videoRejected: "Procedure rejected", videoFailureSummary: "Vertex did not return a procedure. Safe code: {code}.", videoReadySummary: "Review the evidence before allowing any adaptation or execution.", videoReviewedSummary: "The human decision was recorded; no actions were executed.",
    videoVersionLabel: "Version", videoTokenLabel: "Tokens", videoTimeLabel: "Time", videoCallLabel: "Cloud calls", procedureReviewLabel: "PROCEDURE TO REVIEW", procedureRulesLabel: "Rules", procedureExceptionsLabel: "Exceptions", procedureExamplesLabel: "Examples", procedureUncertaintiesLabel: "Uncertainties", procedureNotesLabel: "Optional review notes", rejectProcedure: "Reject", approveProcedure: "Approve procedure", reviewingProcedure: "Recording decision…", emptyEvidence: "Not stated by the source.",
  },
};

const form = document.querySelector("#trainer-form");
const steps = [...document.querySelectorAll(".form-step")];
const markers = [...document.querySelectorAll("[data-step-marker]")];
const taskInput = document.querySelector("#task-description");
const robotModel = document.querySelector("#robot-model");
const computerApplication = document.querySelector("#computer-application");
const sourceQuery = document.querySelector("#source-query");
const sourceCandidates = document.querySelector("#source-candidates");
const searchSourcesButton = document.querySelector("#search-sources");
const approveSourcesButton = document.querySelector("#approve-sources");
const videoUrl = document.querySelector("#video-url");
const videoFile = document.querySelector("#video-file");
const taskError = document.querySelector("#task-error");
const destinationError = document.querySelector("#destination-error");
const sourceError = document.querySelector("#source-error");
const projectFeedback = document.querySelector("#project-feedback");
const processingConsole = document.querySelector("#processing-console");
const processResult = document.querySelector("#process-result");
const processLog = document.querySelector("#process-log");
const processButton = document.querySelector("#demo-processing");
const processSubmit = form.querySelector("button[type='submit']");
const processStages = [...document.querySelectorAll("[data-process-stage]")];
const computerPracticePanel = document.querySelector("#computer-practice-panel");
const computerPracticeForm = document.querySelector("#computer-practice-form");
const browserTargetUrl = document.querySelector("#browser-target-url");
const browserTextSelector = document.querySelector("#browser-text-selector");
const browserSampleText = document.querySelector("#browser-sample-text");
const browserPracticeApproval = document.querySelector("#browser-practice-approval");
const browserPracticeError = document.querySelector("#browser-practice-error");
const runBrowserPracticeButton = document.querySelector("#run-browser-practice");
const practiceEvidence = document.querySelector("#practice-evidence");
const practiceStageElements = [...document.querySelectorAll("[data-practice-stage]")];
const videoProcedurePanel = document.querySelector("#video-procedure-panel");
const videoProcedureSource = document.querySelector("#video-procedure-source");
const videoCostApproval = document.querySelector("#video-cost-approval");
const extractVideoButton = document.querySelector("#extract-video-procedure");
const videoProcedureError = document.querySelector("#video-procedure-error");
const videoProcedureEvidence = document.querySelector("#video-procedure-evidence");
const procedureReview = document.querySelector("#procedure-review");
const approveVideoProcedureButton = document.querySelector("#approve-video-procedure");
const rejectVideoProcedureButton = document.querySelector("#reject-video-procedure");
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
let sourceSearch = null;
let approvedSources = [];
let currentProject = null;
let practiceActiveStage = -1;
let practiceCompletedStages = 0;
let practiceRunResult = null;
let currentVideoSource = null;
let videoProcedureRecord = null;
let videoExtractionRunning = false;

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
  setContent('[data-step="2"] legend', t.destinationLegend);
  document.querySelector(".destination-options").ariaLabel = t.destinationTypeLabel;
  setContent('.destination-option:first-child b', t.robot);
  setContent('.destination-option:first-child small', t.robotCopy);
  setContent('.destination-option:last-child b', t.computer);
  setContent('.destination-option:last-child small', t.computerCopy);
  setContent('label[for="robot-model"]', t.robotModelLabel);
  robotModel.placeholder = t.robotModelPlaceholder;
  setContent("#robot-help", t.robotHelp);
  setContent('label[for="computer-application"]', t.computerAppLabel);
  computerApplication.placeholder = t.computerAppPlaceholder;
  setContent("#computer-help", t.computerHelp);
  setContent('[data-step="2"] [data-back]', t.back);
  setContent('[data-step="2"] [data-next]', t.continue, true);
  setContent('[data-step="3"] legend', t.sourceLegend);
  document.querySelector(".source-options").ariaLabel = t.sourceTypeLabel;
  setContent('[data-source-option="youtube"] small', t.youtubeCopy);
  setContent('[data-source-option="upload"] b', t.upload);
  setContent('[data-source-option="upload"] small', t.uploadCopy);
  setContent('[data-source-option="automatic"] b', t.automatic);
  setContent('[data-source-option="automatic"] small', t.automaticCopy);
  setContent('label[for="video-url"]', t.videoUrlLabel);
  if (!videoFile.files.length) setContent("#file-label", t.selectVideo);
  setContent(".file-drop small", t.fileTypes);
  setContent('label[for="source-query"]', t.searchLabel);
  sourceQuery.placeholder = t.searchPlaceholder;
  setContent("#search-sources", t.searchButton);
  setContent("#search-help", t.searchHelp);
  if (!approveSourcesButton.disabled) setContent("#approve-sources", t.approveSources);
  setContent('[data-step="3"] [data-back]', t.back);
  setContent('[data-step="3"] [data-next]', t.review, true);
  setContent('[data-step="4"] legend', t.reviewLegend);
  document.querySelectorAll(".review-list dt").forEach((label, index) => { label.textContent = t.reviewLabels[index]; });
  setContent(".review-list div:last-child dd", t.dockerDelivery);
  setContent(".honesty-note p", selectedDestination() === "robot" ? t.honestyRobot : t.honestyComputer, true);
  setContent('[data-step="4"] [data-back]', t.edit);
  setContent('[data-step="4"] button[type="submit"]', t.prepareProject, true);
  setContent("#computer-practice-eyebrow", t.practiceEyebrow);
  setContent("#computer-practice-title", t.practiceTitle);
  setContent("#computer-practice-intro", t.practiceIntro);
  setContent("#computer-practice-disclosure", t.practiceDisclosure);
  setContent("#browser-target-label", t.targetLabel);
  browserTargetUrl.placeholder = t.targetPlaceholder;
  setContent("#browser-target-help", t.targetHelp);
  setContent("#browser-selector-label", t.selectorLabel);
  browserTextSelector.placeholder = t.selectorPlaceholder;
  setContent("#browser-selector-help", t.selectorHelp);
  setContent("#browser-sample-label", t.sampleLabel);
  browserSampleText.placeholder = t.samplePlaceholder;
  setContent("#browser-sample-help", t.sampleHelp);
  setContent("#browser-plan-label", t.planLabel);
  setContent("#browser-approval-label", t.approvalLabel);
  setContent("#run-browser-practice", t.runPractice, true);
  setContent("#practice-progress-label", t.practiceProgressLabel);
  setContent("#practice-result-label", t.practiceResultLabel);
  setContent("#practice-actions-label", t.practiceActionsLabel);
  setContent("#practice-network-label", t.practiceNetworkLabel);
  setContent("#practice-blocked-label", t.practiceBlockedLabel);
  setContent("#practice-cloud-label", t.practiceCloudLabel);
  setContent("#video-procedure-eyebrow", t.videoProcedureEyebrow);
  setContent("#video-procedure-title", t.videoProcedureTitle);
  setContent("#video-procedure-intro", t.videoProcedureIntro);
  setContent("#video-source-label", t.videoSourceLabel);
  setContent("#video-cost-label", t.videoCostLabel);
  setContent("#video-extraction-status-label", t.videoStatusLabel);
  setContent("#video-version-label", t.videoVersionLabel);
  setContent("#video-token-label", t.videoTokenLabel);
  setContent("#video-time-label", t.videoTimeLabel);
  setContent("#video-call-label", t.videoCallLabel);
  setContent("#procedure-review-label", t.procedureReviewLabel);
  setContent("#procedure-rules-label", t.procedureRulesLabel);
  setContent("#procedure-exceptions-label", t.procedureExceptionsLabel);
  setContent("#procedure-examples-label", t.procedureExamplesLabel);
  setContent("#procedure-uncertainties-label", t.procedureUncertaintiesLabel);
  setContent("#procedure-notes-label", t.procedureNotesLabel);
  setContent("#reject-video-procedure", t.rejectProcedure);
  setContent("#approve-video-procedure", t.approveProcedure);
  setContent(".privacy-note", t.privacy, true);
  setContent("footer span:last-child", t.footer);
  document.querySelectorAll("[data-language]").forEach((button) => { button.setAttribute("aria-pressed", String(button.dataset.language === currentLanguage)); });
  try { localStorage.setItem("aprendiz-language", currentLanguage); } catch (_) { /* Keep preference in memory. */ }
  updateSystemStatus();
  renderProcessState();
  renderPracticePlan();
  renderPracticeState();
  renderVideoProcedureState();
}

function showStep(stepNumber) {
  currentStep = stepNumber;
  steps.forEach((step) => { const active = Number(step.dataset.step) === stepNumber; step.hidden = !active; step.classList.toggle("is-active", active); });
  markers.forEach((marker) => { const markerStep = Number(marker.dataset.stepMarker); marker.classList.toggle("is-active", markerStep === stepNumber); marker.classList.toggle("is-complete", markerStep < stepNumber); });
  steps.find((step) => Number(step.dataset.step) === stepNumber)?.querySelector("textarea, input:not([type='radio']), button")?.focus({ preventScroll: true });
}

function selectedSourceType() { return form.elements["source-type"].value; }
function selectedDestination() { return form.elements.destination.value; }

function validateCurrentStep() {
  const t = translations[currentLanguage];
  if (currentStep === 1) {
    const valid = taskInput.value.trim().length >= 12;
    taskError.textContent = valid ? "" : t.taskError;
    taskInput.setAttribute("aria-invalid", String(!valid));
    return valid;
  }
  if (currentStep === 2) {
    const destination = selectedDestination();
    const target = destination === "robot" ? robotModel : computerApplication;
    const valid = target.value.trim().length >= 2;
    destinationError.textContent = valid ? "" : destination === "robot" ? t.robotModelError : t.computerAppError;
    target.setAttribute("aria-invalid", String(!valid));
    return valid;
  }
  if (currentStep === 3) {
    const type = selectedSourceType();
    const valid = Boolean(
      (type === "youtube" && videoUrl.value.trim() && videoUrl.checkValidity())
      || (type === "upload" && videoFile.files.length > 0)
      || (type === "automatic" && approvedSources.length > 0)
    );
    sourceError.textContent = valid ? "" : type === "youtube" ? t.urlError : type === "upload" ? t.fileError : t.automaticError;
    return valid;
  }
  return true;
}

function fillReview() {
  const t = translations[currentLanguage];
  const destination = selectedDestination();
  const sourceType = selectedSourceType();
  const source = sourceType === "youtube"
    ? videoUrl.value.trim()
    : sourceType === "upload"
      ? videoFile.files[0]?.name
      : approvedSources.map((item) => item.title).join(" · ");
  setContent("#review-task", taskInput.value.trim());
  setContent("#review-destination", destination === "robot" ? t.robotReview : t.computerReview);
  setContent("#review-configuration", destination === "robot" ? `${robotModel.value.trim()} · ${t.robotConfig}` : `${computerApplication.value.trim()} · ${t.computerConfig}`);
  setContent("#review-source", source || t.noSource);
  setContent(".honesty-note p", destination === "robot" ? t.honestyRobot : t.honestyComputer, true);
}

function renderSourceStatus(message, isError = false) {
  sourceCandidates.innerHTML = "";
  const status = document.createElement("p");
  status.className = `source-search-status${isError ? " is-error" : ""}`;
  status.textContent = message;
  sourceCandidates.append(status);
}

function renderSourceCandidates(candidates) {
  const t = translations[currentLanguage];
  sourceCandidates.innerHTML = "";
  if (!candidates.length) {
    renderSourceStatus(t.searchEmpty);
    approveSourcesButton.hidden = true;
    return;
  }
  candidates.forEach((candidate) => {
    const card = document.createElement("label");
    card.className = "source-candidate";
    const imageElement = document.createElement("img");
    imageElement.alt = "";
    imageElement.loading = "lazy";
    if (candidate.thumbnail_url) imageElement.src = candidate.thumbnail_url;
    const copy = document.createElement("span");
    const title = document.createElement("b");
    title.textContent = candidate.title;
    const channel = document.createElement("small");
    channel.textContent = candidate.channel;
    const summary = document.createElement("p");
    summary.textContent = candidate.summary;
    copy.append(title, channel, summary);
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "source-candidate";
    checkbox.value = candidate.video_id;
    checkbox.setAttribute("aria-label", candidate.title);
    card.append(imageElement, copy, checkbox);
    sourceCandidates.append(card);
  });
  approveSourcesButton.hidden = false;
  approveSourcesButton.disabled = false;
  setContent("#approve-sources", t.approveSources);
}

async function searchAutomaticSources() {
  const t = translations[currentLanguage];
  const query = sourceQuery.value.trim();
  if (query.length < 3) {
    renderSourceStatus(t.automaticError, true);
    return;
  }
  approvedSources = [];
  sourceSearch = null;
  searchSourcesButton.disabled = true;
  approveSourcesButton.hidden = true;
  setContent("#search-sources", t.searching);
  renderSourceStatus(t.searching);
  try {
    const response = await fetch("/api/sources/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        language: currentLanguage,
        max_results: 3,
        acknowledge_search_quota: true,
      }),
    });
    if (!response.ok) throw new Error(`Source search failed: ${response.status}`);
    sourceSearch = await response.json();
    renderSourceCandidates(sourceSearch.candidates);
  } catch (error) {
    renderSourceStatus(t.searchUnavailable, true);
    console.error(error);
  } finally {
    searchSourcesButton.disabled = false;
    setContent("#search-sources", t.searchButton);
  }
}

async function approveAutomaticSources() {
  const t = translations[currentLanguage];
  const selectedIds = [...document.querySelectorAll("input[name='source-candidate']:checked")].map((input) => input.value);
  if (!sourceSearch || !selectedIds.length) {
    sourceError.textContent = t.selectCandidate;
    return;
  }
  approveSourcesButton.disabled = true;
  setContent("#approve-sources", t.approving);
  try {
    const response = await fetch(`/api/sources/search/${encodeURIComponent(sourceSearch.search_id)}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_ids: selectedIds }),
    });
    if (!response.ok) throw new Error(`Source approval failed: ${response.status}`);
    const result = await response.json();
    approvedSources = result.approved_sources;
    renderSourceStatus(t.sourceApproved.replace("{count}", String(approvedSources.length)));
    approveSourcesButton.hidden = true;
    sourceError.textContent = "";
  } catch (error) {
    renderSourceStatus(t.searchUnavailable, true);
    approveSourcesButton.hidden = true;
    console.error(error);
  }
}

function showProjectFeedback(message, isError = false) {
  projectFeedback.textContent = message;
  projectFeedback.hidden = false;
  projectFeedback.classList.toggle("is-error", isError);
}

function buildPracticeActions() {
  const actions = [{ action_id: "open-target", kind: "navigate", target: browserTargetUrl.value.trim() }];
  const selector = browserTextSelector.value.trim();
  const sampleText = browserSampleText.value;
  if (selector && sampleText) {
    actions.push({ action_id: "enter-sample", kind: "type_text", target: selector, value_template: sampleText });
  }
  return actions;
}

function validatedPracticeTarget() {
  try {
    const target = new URL(browserTargetUrl.value.trim());
    const standardPort = !target.port
      || (target.protocol === "http:" && target.port === "80")
      || (target.protocol === "https:" && target.port === "443");
    if (!["http:", "https:"].includes(target.protocol) || !target.hostname || target.username || target.password || !standardPort) return null;
    return target;
  } catch (_) {
    return null;
  }
}

function renderPracticePlan() {
  const t = translations[currentLanguage];
  const preview = document.querySelector("#browser-plan-preview");
  if (!preview) return;
  preview.innerHTML = "";
  const target = validatedPracticeTarget();
  const planned = target
    ? [t.planNavigate.replace("{url}", target.href)]
    : [t.planEmpty];
  if (browserTextSelector?.value.trim() && browserSampleText?.value) {
    planned.push(t.planType.replace("{selector}", browserTextSelector.value.trim()));
  }
  planned.forEach((description, index) => {
    const item = document.createElement("li");
    const number = document.createElement("span");
    number.textContent = String(index + 1).padStart(2, "0");
    const copy = document.createElement("p");
    copy.textContent = description;
    item.append(number, copy);
    preview.append(item);
  });
}

function localizedPracticeStatus(status) {
  const t = translations[currentLanguage];
  return {
    completed: t.practiceComplete,
    partially_completed: t.practicePartial,
    blocked: t.practiceBlocked,
    rejected: t.practiceRejected,
  }[status] || t.practiceWaiting;
}

function renderPracticeState() {
  if (!practiceStageElements.length) return;
  const t = translations[currentLanguage];
  practiceStageElements.forEach((item, index) => {
    const complete = index < practiceCompletedStages;
    const active = index === practiceActiveStage;
    item.classList.toggle("is-complete", complete);
    item.classList.toggle("is-active", active);
    item.querySelector("b").textContent = t.practiceStages[index][0];
    item.querySelector("small").textContent = complete ? t.practiceDone : active ? t.practiceActive : t.practiceStages[index][1];
  });
  if (runBrowserPracticeButton.disabled) setContent("#run-browser-practice", t.practiceRunning);
  else setContent("#run-browser-practice", t.runPractice, true);

  const execution = practiceRunResult?.execution;
  setContent("#practice-result-status", execution ? localizedPracticeStatus(execution.status) : practiceActiveStage >= 0 ? t.practiceRunning : t.practiceWaiting);
  setContent("#practice-result-summary", execution ? (execution.status === "completed" ? t.practiceSuccessSummary : t.practiceFailureSummary) : "");
  const completedActions = execution?.actions?.filter((action) => action.status === "completed").length || 0;
  setContent("#practice-actions-count", `${completedActions}/${execution?.actions?.length || 0}`);
  setContent("#practice-network-count", String(execution?.external_network_requests || 0));
  setContent("#practice-blocked-count", String(execution?.blocked_network_requests || 0));
  setContent("#practice-cloud-count", String(execution?.cloud_calls_made || 0));

  const actionResults = document.querySelector("#practice-action-results");
  actionResults.innerHTML = "";
  const evidenceItems = execution?.actions?.length ? execution.actions : execution?.violations || [];
  evidenceItems.forEach((evidence) => {
    const item = document.createElement("li");
    if (typeof evidence === "string") {
      item.textContent = evidence;
    } else {
      const state = document.createElement("b");
      state.textContent = evidence.status;
      const description = document.createTextNode(`${evidence.kind} · ${evidence.observed_url || evidence.target}`);
      item.append(state, description);
    }
    actionResults.append(item);
  });
}

function apiErrorMessage(payload, fallback) {
  const detail = payload?.detail;
  if (typeof detail === "string") return detail;
  if (detail?.violations?.length) return detail.violations.join(" ");
  return fallback;
}

function renderProcedureList(selector, values) {
  const t = translations[currentLanguage];
  const list = document.querySelector(selector);
  list.innerHTML = "";
  (values?.length ? values : [t.emptyEvidence]).forEach((value) => {
    const item = document.createElement("li");
    item.textContent = value;
    list.append(item);
  });
}

function renderExtractedProcedure(procedure) {
  setContent("#procedure-task", procedure.task);
  setContent("#procedure-objective", procedure.objective);
  const stepsList = document.querySelector("#procedure-steps");
  stepsList.innerHTML = "";
  procedure.steps.forEach((step) => {
    const item = document.createElement("li");
    const action = document.createElement("span");
    action.textContent = step.action;
    item.append(action);
    const evidenceParts = [...(step.source_timestamps || [])];
    if (step.evidence) evidenceParts.push(step.evidence);
    if (evidenceParts.length) {
      const evidence = document.createElement("small");
      evidence.textContent = evidenceParts.join(" · ");
      item.append(evidence);
    }
    stepsList.append(item);
  });
  renderProcedureList("#procedure-rules", procedure.rules);
  renderProcedureList("#procedure-exceptions", procedure.exceptions);
  renderProcedureList("#procedure-examples", procedure.examples);
  renderProcedureList("#procedure-uncertainties", procedure.uncertainties);
}

function localizedVideoStatus(status) {
  const t = translations[currentLanguage];
  return {
    extraction_failed: t.videoFailed,
    awaiting_review: t.videoAwaitingReview,
    approved: t.videoApproved,
    rejected: t.videoRejected,
  }[status] || (videoExtractionRunning ? t.videoRunning : t.videoWaiting);
}

function renderVideoProcedureState() {
  if (!videoProcedurePanel) return;
  const t = translations[currentLanguage];
  setContent("#extract-video-procedure", videoExtractionRunning ? t.extractingVideo : t.extractVideo, !videoExtractionRunning);
  const retryableFailure = videoProcedureRecord?.status === "extraction_failed";
  extractVideoButton.disabled = videoExtractionRunning || Boolean(videoProcedureRecord && !retryableFailure);
  videoProcedureEvidence.hidden = !videoExtractionRunning && !videoProcedureRecord;
  setContent("#video-extraction-status", localizedVideoStatus(videoProcedureRecord?.status));

  if (!videoProcedureRecord) {
    setContent("#video-extraction-summary", videoExtractionRunning ? t.videoReadySummary : "");
    setContent("#video-version", "—");
    setContent("#video-tokens", "—");
    setContent("#video-time", "—");
    setContent("#video-calls", "0");
    procedureReview.hidden = true;
    return;
  }

  const record = videoProcedureRecord;
  const failed = record.status === "extraction_failed";
  const reviewed = ["approved", "rejected"].includes(record.status);
  setContent(
    "#video-extraction-summary",
    failed
      ? t.videoFailureSummary.replace("{code}", record.failure_code || "provider_error")
      : reviewed ? t.videoReviewedSummary : t.videoReadySummary,
  );
  setContent("#video-version", record.procedure_version ? `V${record.procedure_version}` : "—");
  setContent("#video-tokens", record.usage?.total_tokens ?? "—");
  setContent("#video-time", record.elapsed_seconds == null ? "—" : `${record.elapsed_seconds}s`);
  setContent("#video-calls", String(record.cloud_calls_made));
  procedureReview.hidden = !record.procedure;
  if (record.procedure) renderExtractedProcedure(record.procedure);
  const canReview = record.status === "awaiting_review";
  approveVideoProcedureButton.disabled = !canReview;
  rejectVideoProcedureButton.disabled = !canReview;
}

function configureVideoProcedure(project, sourceUrl) {
  currentProject = project;
  currentVideoSource = sourceUrl;
  videoProcedureRecord = null;
  videoExtractionRunning = false;
  videoCostApproval.checked = false;
  videoProcedureError.textContent = "";
  videoProcedureEvidence.hidden = true;
  videoProcedurePanel.hidden = !sourceUrl;
  if (sourceUrl) {
    videoProcedureSource.href = sourceUrl;
    videoProcedureSource.textContent = sourceUrl;
  }
  renderVideoProcedureState();
}

async function extractProjectVideoProcedure() {
  const t = translations[currentLanguage];
  videoProcedureError.textContent = "";
  if (!currentProject || !currentVideoSource || !videoCostApproval.checked) {
    videoProcedureError.textContent = t.videoCostError;
    return;
  }
  videoExtractionRunning = true;
  renderVideoProcedureState();
  await nextPaint();
  try {
    const response = await fetch(`/api/projects/${encodeURIComponent(currentProject.project_id)}/video-procedures/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        video_url: currentVideoSource,
        task_hint: taskInput.value.trim(),
        output_language: currentLanguage,
        acknowledge_source_approved: true,
        acknowledge_cloud_cost: true,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(apiErrorMessage(payload, t.videoExtractionError));
    videoProcedureRecord = payload;
  } catch (error) {
    videoProcedureError.textContent = error.message || t.videoExtractionError;
    console.error(error);
  } finally {
    videoExtractionRunning = false;
    if (videoProcedureRecord?.status === "extraction_failed") videoCostApproval.checked = false;
    renderVideoProcedureState();
  }
}

async function reviewProjectVideoProcedure(decision) {
  const t = translations[currentLanguage];
  if (!currentProject || !videoProcedureRecord) return;
  approveVideoProcedureButton.disabled = true;
  rejectVideoProcedureButton.disabled = true;
  setContent(decision === "approve" ? "#approve-video-procedure" : "#reject-video-procedure", t.reviewingProcedure);
  try {
    const response = await fetch(`/api/projects/${encodeURIComponent(currentProject.project_id)}/video-procedures/${encodeURIComponent(videoProcedureRecord.extraction_id)}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision,
        notes: document.querySelector("#procedure-review-notes").value.trim() || null,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(apiErrorMessage(payload, t.videoExtractionError));
    videoProcedureRecord = payload;
  } catch (error) {
    videoProcedureError.textContent = error.message || t.videoExtractionError;
    console.error(error);
  } finally {
    setContent("#approve-video-procedure", t.approveProcedure);
    setContent("#reject-video-procedure", t.rejectProcedure);
    renderVideoProcedureState();
  }
}

async function nextPaint() {
  await new Promise((resolve) => requestAnimationFrame(() => resolve()));
}

async function runComputerPractice() {
  const t = translations[currentLanguage];
  browserPracticeError.textContent = "";
  const target = validatedPracticeTarget();
  const selector = browserTextSelector.value.trim();
  const sampleText = browserSampleText.value;
  if (!target) {
    browserPracticeError.textContent = t.practiceUrlError;
    return;
  }
  if (Boolean(selector) !== Boolean(sampleText)) {
    browserPracticeError.textContent = t.practicePairError;
    return;
  }
  if (!browserPracticeApproval.checked || !currentProject) {
    browserPracticeError.textContent = t.practiceApprovalError;
    return;
  }

  practiceEvidence.hidden = false;
  practiceRunResult = null;
  practiceCompletedStages = 0;
  practiceActiveStage = 0;
  runBrowserPracticeButton.disabled = true;
  renderPracticeState();
  practiceEvidence.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "nearest" });
  await nextPaint();

  try {
    const draftResponse = await fetch(`/api/projects/${encodeURIComponent(currentProject.project_id)}/computer-practices`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        procedure_name: taskInput.value.trim().slice(0, 160),
        plan_origin: "user_reviewed",
        actions: buildPracticeActions(),
        approved_hosts: [target.hostname],
      }),
    });
    const draftPayload = await draftResponse.json();
    if (!draftResponse.ok) throw new Error(apiErrorMessage(draftPayload, t.practiceGenericError));
    practiceCompletedStages = 2;
    practiceActiveStage = 2;
    renderPracticeState();
    await nextPaint();

    const executionResponse = await fetch(`/api/projects/${encodeURIComponent(currentProject.project_id)}/computer-practices/${encodeURIComponent(draftPayload.practice_id)}/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        acknowledge_actions_reviewed: true,
        acknowledge_external_network: true,
        action_timeout_ms: 10000,
      }),
    });
    const executionPayload = await executionResponse.json();
    if (!executionResponse.ok) throw new Error(apiErrorMessage(executionPayload, t.practiceGenericError));
    practiceCompletedStages = 4;
    practiceActiveStage = -1;
    practiceRunResult = executionPayload;
    renderPracticeState();
  } catch (error) {
    practiceActiveStage = -1;
    browserPracticeError.textContent = error.message || t.practiceGenericError;
    renderPracticeState();
    console.error(error);
  } finally {
    runBrowserPracticeButton.disabled = false;
    renderPracticeState();
  }
}

async function prepareProject() {
  const t = translations[currentLanguage];
  const destination = selectedDestination();
  const sourceType = selectedSourceType();
  const source = sourceType === "youtube"
    ? videoUrl.value.trim()
    : sourceType === "upload"
      ? videoFile.files[0]?.name
      : approvedSources.map((item) => item.url).join(", ");
  projectFeedback.hidden = true;
  processSubmit.disabled = true;
  try {
    const payload = {
      task_description: taskInput.value.trim(),
      destination,
      language: currentLanguage,
    };
    if (destination === "robot") {
      payload.robot_model = robotModel.value.trim();
    } else {
      payload.computer_application = computerApplication.value.trim();
    }
    const response = await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`Project creation failed: ${response.status}`);
    const project = await response.json();
    if (!project.is_sufficiently_clear) {
      showProjectFeedback(project.clarification_questions[0]?.question || t.projectError, true);
      return;
    }
    const readyMessage = destination === "robot" ? t.projectReadyRobot : t.projectReadyComputer;
    showProjectFeedback(readyMessage.replace("{id}", project.project_id));
    const extractionSource = sourceType === "youtube"
      ? videoUrl.value.trim()
      : sourceType === "automatic" ? approvedSources[0]?.url : null;
    configureVideoProcedure(project, extractionSource);
    if (destination === "robot") {
      computerPracticePanel.hidden = true;
      window.setTimeout(() => startProcessing(taskInput.value.trim(), source), reducedMotion.matches ? 0 : 550);
    } else {
      computerPracticePanel.hidden = false;
      browserPracticeApproval.checked = false;
      practiceEvidence.hidden = true;
      practiceRunResult = null;
      practiceActiveStage = -1;
      practiceCompletedStages = 0;
      renderPracticePlan();
      renderPracticeState();
      window.setTimeout(() => computerPracticePanel.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "start" }), reducedMotion.matches ? 0 : 350);
    }
  } catch (error) {
    showProjectFeedback(t.projectError, true);
    console.error(error);
  } finally {
    processSubmit.disabled = false;
  }
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
  if (nextButton && validateCurrentStep()) { if (currentStep === 3) fillReview(); showStep(Math.min(4, currentStep + 1)); }
  if (backButton) showStep(Math.max(1, currentStep - 1));
});

document.querySelectorAll("input[name='destination']").forEach((radio) => {
  radio.addEventListener("change", () => {
    document.querySelectorAll(".destination-option").forEach((option) => option.classList.toggle("is-selected", option.contains(radio)));
    document.querySelectorAll("[data-destination-panel]").forEach((panel) => { panel.hidden = panel.dataset.destinationPanel !== radio.value; });
    destinationError.textContent = "";
    projectFeedback.hidden = true;
    currentProject = null;
    computerPracticePanel.hidden = true;
    videoProcedurePanel.hidden = true;
  });
});

document.querySelectorAll("input[name='source-type']").forEach((radio) => {
  radio.addEventListener("change", () => {
    document.querySelectorAll(".source-option").forEach((option) => option.classList.toggle("is-selected", option.contains(radio)));
    document.querySelectorAll("[data-source-panel]").forEach((panel) => { panel.hidden = panel.dataset.sourcePanel !== radio.value; });
    if (radio.value === "automatic" && !sourceQuery.value.trim()) sourceQuery.value = taskInput.value.trim();
    sourceError.textContent = "";
    currentProject = null;
    computerPracticePanel.hidden = true;
    videoProcedurePanel.hidden = true;
  });
});

videoFile.addEventListener("change", () => setContent("#file-label", videoFile.files[0]?.name || translations[currentLanguage].selectVideo));
sourceQuery.addEventListener("input", () => {
  sourceSearch = null;
  approvedSources = [];
  sourceCandidates.innerHTML = "";
  approveSourcesButton.hidden = true;
  sourceError.textContent = "";
});
searchSourcesButton.addEventListener("click", searchAutomaticSources);
approveSourcesButton.addEventListener("click", approveAutomaticSources);
form.addEventListener("submit", (event) => { event.preventDefault(); prepareProject(); });
computerPracticeForm.addEventListener("submit", (event) => { event.preventDefault(); runComputerPractice(); });
extractVideoButton.addEventListener("click", extractProjectVideoProcedure);
approveVideoProcedureButton.addEventListener("click", () => reviewProjectVideoProcedure("approve"));
rejectVideoProcedureButton.addEventListener("click", () => reviewProjectVideoProcedure("reject"));
[browserTargetUrl, browserTextSelector, browserSampleText].forEach((input) => input.addEventListener("input", () => {
  browserPracticeApproval.checked = false;
  browserPracticeError.textContent = "";
  renderPracticePlan();
}));
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
