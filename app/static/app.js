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
    idleStatus: "Listo para iniciar", readyStatus: "Simulación completada", sourceTag: "TRAYECTORIA INTERNA · NO ES EL VIDEO", demoTask: "Recoger y colocar una pieza frágil", builtInTrajectory: "{robot} · demostración interna", builtInTrajectoryIdle: "Trayectoria interna de demostración",
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
    workspaceLabel: "APRENDIZ / ESPACIO DE TRABAJO", workspaceViewLabel: "Vista del espacio de trabajo", workspaceViews: ["Enseñar", "Configurar", "Video", "Práctica", "Simulación"], workspaceClose: "Cerrar espacio de trabajo", spendTokenLabel: "Token de gasto", spendTokenPlaceholder: "Pega el token", spendTokenMissing: "Este despliegue exige un token de gasto. Pégalo en la barra superior antes de continuar.", spendTokenRejected: "El servidor rechazó el token de gasto. Lo más probable es que se haya rotado: pega el actual en la barra de arriba y vuelve a intentarlo.", httpFailure: "El servidor respondió {status} sin dar explicación.", approveFailed: "No se pudo aprobar la selección: {detail}", projectFailed: "No se pudo preparar el proyecto: {detail}", processFailedDetail: "El backend no pudo completar la sesión: {detail}", networkFailure: "No se pudo contactar con el servidor.", spendRemaining: "Quedan {amount} {currency}", spendTooltip: "Gastado {spent} de {ceiling} {currency} en {period}, con {calls} llamada(s) de pago.", spendExhausted: "Tope de {currency} agotado", spendCeilingReached: "Se alcanzó el tope de gasto de esta aplicación. No se hará ninguna llamada más hasta que subas el tope o empiece el mes siguiente.", workspaceContexts: { teach: "Enseñar al agente", setup: "Configuración avanzada", video: "Revisión del video", practice: "Práctica aislada", simulation: "Simulación local" }, procedurePrevious: "Paso anterior", procedureNext: "Paso siguiente",
    formProgressLabel: "Progreso de configuración", formMarkers: ["Tarea", "Destino", "Fuente", "Revisar"], taskLegend: "Describe el resultado que necesitas", taskLabel: "Tarea del agente",
    taskPlaceholder: "Ej.: Enseñar a un brazo robótico a recoger y colocar una pieza frágil.", taskHelp: "Describe el resultado y los límites importantes. Esta primera sesión se ejecutará únicamente en simulación.",
    continue: "Continuar <span aria-hidden=\"true\">→</span>", destinationLegend: "¿Dónde ejecutará lo aprendido?", destinationTypeLabel: "Destino de ejecución",
    robot: "Robot", robotCopy: "Movimiento validado primero en simulación", computer: "Computadora", computerCopy: "Procedimiento aislado antes de ejecutarlo",
    robotModelLabel: "Marca y modelo exacto", robotModelPlaceholder: "Ej.: Unitree Go2", robotHelp: "Usaremos ARP-1 y seleccionaremos el simulador compatible automáticamente.",
    computerAppLabel: "Aplicación objetivo", computerAppPlaceholder: "Ej.: Google Chrome, Excel o Blender", computerHelp: "El sistema operativo se detectará automáticamente y la primera ejecución será aislada.",
    sourceLegend: "Añade una referencia para la futura demostración", sourceTypeLabel: "Tipo de fuente",
    youtubeCopy: "Referencia a un video instructivo", upload: "Video local", uploadCopy: "Se guarda aquí, nunca se envía", automatic: "Búsqueda automática", automaticCopy: "Encuentra referencias para que las apruebes", videoUrlLabel: "Enlace de referencia",
    searchLabel: "¿Qué demostración debe buscar?", searchPlaceholder: "Ej.: perro corriendo vista lateral biomecánica", searchButton: "Buscar referencias", searching: "Buscando…", searchHelp: "La búsqueda usa una llamada acotada; ningún video se analiza hasta que lo apruebes.", approveSources: "Aprobar selección", approving: "Aprobando…", sourceApproved: "{count} referencia(s) aprobada(s). El análisis aún no ha comenzado.", searchEmpty: "No se encontraron videos para esta búsqueda.", searchUnavailable: "La búsqueda automática no está configurada todavía. Puedes usar un enlace directo mientras se habilita YouTube Data API.", selectCandidate: "Selecciona al menos una referencia antes de aprobar.",
    selectVideo: "Selecciona un video", fileTypes: "MP4, MOV, WEBM o MKV",
    uploadNote: "El archivo se guarda en esta máquina y nunca se envía a un modelo en la nube. Todavía no se puede extraer un procedimiento de un archivo local: para eso hace falta una URL pública de YouTube.",
    uploadStore: "Guardar en esta máquina",
    uploadStoring: "Guardando…",
    uploadNeedsProject: "Crea el proyecto antes de guardar un video.",
    uploadRemove: "Eliminar",
    uploadMeta: "{size} · sha256 {hash} · no enviado",
    uploadFailed: "No se pudo guardar el video: {detail}",
    historyLabel: "HISTORIAL DE VERSIONES",
    historyTotals: "{versions} versiones \u00b7 {calls} llamadas a la nube \u00b7 {tokens} tokens",
    historyVersion: "V{version}",
    historyVersionMeta: "{steps} pasos \u00b7 {status}",
    historyDiffLabel: "V{from} \u2192 V{to}",
    historyNoChanges: "Ninguna diferencia entre estas dos versiones.",
    historyDiffSummary: "{changed} cambiados \u00b7 {added} a\u00f1adidos \u00b7 {removed} eliminados \u00b7 {unchanged} iguales.",
    historySameSource: "Ambas versiones vienen del mismo video.",
    historyCrossSource: "Estas versiones vienen de videos distintos.",
    historyStepChanged: "Paso {step}:",
    historyStepAdded: "Paso {step} a\u00f1adido: {after}",
    historyStepRemoved: "Paso {step} eliminado: {before}",
    historyListAdded: "{field} a\u00f1adido: {value}",
    historyListRemoved: "{field} eliminado: {value}",
    reconciliationLabel: "RECONCILIACI\u00d3N",
    reconciliationSummary: "{sources} fuentes aprobadas \u00b7 {distinct} videos distintos \u00b7 confianza {confidence} \u00b7 {conflicts} contradicciones.",
    reconciliationNone: "Aprueba una segunda extracci\u00f3n para poder reconciliar.", back: "← Atrás", review: "Revisar <span aria-hidden=\"true\">→</span>",
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
    adaptationSummary: "{actionable} de {total} pasos podrían ejecutarse en este destino.",
    adaptationMissing: "Falta: {missing}", adaptationBlocked: "Nada se ejecuta sin tu aprobación explícita.",
    motionLabel: "EVIDENCIA DE MOVIMIENTO",
    motionIntro: "Los pasos en prosa nunca se vuelven una trayectoria. Este análisis muestrea {fps} fps durante {window} s del video ya aprobado y devuelve ángulos de articulación con marca de tiempo.",
    motionAck: "Entiendo que esto gasta una llamada a la nube sobre la fuente que ya aprobaste.",
    motionRun: "Analizar movimiento (1 llamada)",
    motionRunning: "Analizando movimiento…",
    motionVerdictUsable: "Muestras utilizables",
    motionVerdictSuspect: "Muestras sospechosas",
    motionVerdictNotEvidence: "Esto no es evidencia",
    motionStats: "{samples} muestras · {joints} articulaciones · {span} s observados · {rate} muestras/s · confianza media {confidence} · {tokens} tokens · {elapsed} s",
    motionEstimate: "Ángulos estimados por un modelo de visión, no medidos.",
    motionFinding: {
      no_samples: "El análisis no devolvió ninguna muestra articular utilizable.",
      mirrored_sides: "Izquierda y derecha traen exactamente el mismo ángulo en {identical} de {paired} lecturas emparejadas. Dos piernas de un cuerpo que camina no se mueven igual, así que estos lados no son observaciones independientes.",
      uniform_confidence: "Las {samples} muestras informan la misma confianza {confidence}, así que la confianza no distingue nada y no se estimó muestra por muestra.",
      uniform_visibility: "Las {samples} muestras informan la misma visibilidad «{visibility}», así que la oclusión no se juzgó cuadro por cuadro.",
      acyclic_all: "Cada articulación medida ({joints}) traza una sola subida y bajada en toda la ventana de {window} s. Caminar se repite cerca de una vez por segundo, así que un solo arco es una curva dibujada, no un ciclo de marcha medido.",
      acyclic_some: "{flagged} de {checked} articulaciones ({joints}) oscilan mucho pero cambian de dirección como máximo una vez en la ventana.",
    },
    motionFailed: "El análisis de movimiento falló: {detail}",
    motionBudget: "Petición rechazada antes de gastar: {detail}",
    recentWorkLabel: "TRABAJO GUARDADO", recentWorkNote: "Guardado en este equipo. Ábrelo para continuar donde lo dejaste.",
    recentWorkOpen: "Abrir {task}", recentWorkRobot: "Robot", recentWorkComputer: "Computadora",
    recentWorkApproved: "Procedimiento aprobado", recentWorkRejected: "Procedimiento rechazado", recentWorkAwaiting: "Pendiente de revisión",
    recentWorkFailed: "Extracción fallida", recentWorkNoExtraction: "Sin extracción", recentWorkOpened: "Proyecto {id} restaurado desde el almacenamiento local.",
    extractionActivityNote: "Una llamada acotada a Vertex sigue en curso. No cierres esta vista.",
    nextStepLabel: "SIGUIENTE PASO", nextStepAwaitingReview: "Revisa los pasos y después aprueba o rechaza el procedimiento.",
    nextStepApprovedRobot: "Aprobado. Ahora valida el movimiento en la simulación local. Esa simulación usa una trayectoria interna, no el video.",
    nextStepSimulate: "Validar en simulación",
    teachEyebrow: "ENSEÑAR AL AGENTE",
    teachTitle: "Dile qué debe aprender y de qué video.",
    teachTaskLabel: "¿Qué debe aprender?",
    teachTaskPlaceholder: "Ej.: Cómo funciona un brazo humano, para que lo aprenda un robot.", teachTargetPlaceholderRobot: "Ej.: APRENDIZ SimArm-6", teachTargetPlaceholderComputer: "Ej.: Google Chrome",
    teachUrlLabel: "Enlace del video (YouTube)",
    teachUrlPlaceholder: "https://youtube.com/…",
    teachDestinationLabel: "¿Dónde se ejecutará?",
    teachRobot: "Robot", teachRobotHelp: "Se valida en simulación local.",
    teachComputer: "Computadora", teachComputerHelp: "Ensayo aislado en el navegador.",
    teachTargetRobot: "Modelo exacto del robot", teachTargetComputer: "Aplicación en la computadora", teachTargetError: "Indica el modelo exacto del robot o la aplicación (al menos 2 caracteres).",
    teachConsent: "Autorizo hasta {calls} llamada(s) de pago a Vertex para este aprendizaje. Quedan {remaining}.",
    teachConsentNoCeiling: "Autorizo hasta {calls} llamada(s) de pago a Vertex para este aprendizaje.",
    teachAdvanced: "Configuración avanzada", teachStart: "Enseñar al agente",
    teachTaskError: "Describe la tarea con al menos 12 caracteres.",
    teachUrlError: "Pega un enlace válido que empiece por http.",
    teachConsentError: "Marca la autorización antes de continuar.",
    teachProgressLabel: "EL AGENTE ESTÁ TRABAJANDO",
    teachStages: {
      project: ["Preparar el proyecto", "Registra la tarea y el destino"],
      extract: ["Extraer el procedimiento del video", "Una llamada acotada a Vertex"],
      review: ["Tu aprobación", "Nada se adapta ni se ejecuta sin ella"],
      adapt: ["Adaptar al destino", "Qué podría correr y qué falta"],
      motion: ["Analizar el movimiento", "Una llamada acotada a Vertex"],
      ready: ["Listo", "Tu agente está preparado para descargar"],
    },
    teachStates: { pending: "Pendiente", running: "En curso", waiting: "Esperándote", done: "Hecho", failed: "Falló" },
    teachRetry: "Volver al formulario",
    teachApprovalLabel: "ESTO ES LO QUE APRENDIÓ — ¿LO APRUEBAS?",
    teachReject: "Rechazar", teachApprove: "Aprobar",
    teachRejected: "Rechazaste el procedimiento. Puedes volver a enseñar; sería una nueva llamada de pago.",
    teachReviewError: "No se pudo registrar tu decisión.",
    teachResultEyebrow: "TU AGENTE",
    teachNoPlan: "No hay plan de adaptación disponible.",
    teachMotionFailed: "El análisis de movimiento no se completó: {detail} El agente se puede descargar igual, sin esa evidencia.",
    teachViewDetail: "Ver detalle", teachViewSimulation: "Simulación", teachDownload: "Descargar agente",
    teachDownloading: "Preparando el paquete…",
    teachDownloadNote: "Un paquete Docker autocontenido. Quien tenga Docker lo arranca con start.sh o start.ps1; no necesita nada más.",
    teachDownloaded: "Descargado {name} ({files} archivos). Descomprímelo y ejecuta start.sh o start.ps1.",
    simulationEyebrow: "SIMULACIÓN LOCAL",
    simulationTitle: "Lo aprendido del video, y lo que la simulación realmente corre.",
    simulationLearnedLabel: "LO QUE SE APRENDIÓ DEL VIDEO",
    simulationLearnedNote: "{count} pasos extraídos de la fuente que aprobaste, con la marca de tiempo del video de la que salió cada uno.",
    simulationLearnedEmpty: "Todavía no hay procedimiento aprobado para esta sesión.",
    simulationMotionLabel: "MOVIMIENTO OBSERVADO",
    simulationMotionNone: "No has analizado el movimiento del video todavía. Ese análisis vive en la vista Video y gasta una llamada.",
    simulationMotionSummary: "{subject} · cadena {chain} · {samples} muestras de {joints} articulaciones en {span} s · confianza media {confidence}.",
    observedTag: "DEL VIDEO · ÁNGULOS ESTIMADOS",
    observedTagRejected: "DEL VIDEO · MUESTRAS RECHAZADAS",
    observedTagSuspect: "DEL VIDEO · MUESTRAS SOSPECHOSAS",
    observedTitle: "Ángulos de articulación observados en el video",
    observedDescription: "{joints} articulaciones observadas durante {duration} s, cada una dibujada como su propio ángulo en el tiempo.",
    observedSummary: "Esto sí sale de tu video: {joints} articulaciones, {duration} s, {points} lecturas. Cada línea es un ángulo, no un cuerpo.",
    observedSummaryUnverified: "{joints} articulaciones, {duration} s, {points} lecturas devueltas por el modelo. Cada línea es un ángulo, no un cuerpo.",
    observedVerdictNotEvidence: "La auditoría aritmética rechazó estas muestras: no son observaciones. Lo dibujado abajo es lo que el modelo devolvió, no lo que hizo el cuerpo del video. Las razones están en la vista Video.",
    observedVerdictSuspect: "La auditoría marcó estas muestras como sospechosas. Léelas como borrador del modelo, no como medición. Las razones están en la vista Video.",
    observedOmitted: " Se omitieron {count} articulaciones que se movieron menos.",
    observedLegend: "Ángulos estimados por un modelo de visión, no medidos. Las líneas se cortan donde la articulación dejó de verse: ese hueco no se rellena. No se reconstruye el cuerpo porque las muestras no dicen dónde está cada parte ni cuánto mide.",
    observedPlay: "Reproducir el movimiento observado",
    observedPause: "Pausar el movimiento observado",
    observedScrubberLabel: "Momento del movimiento observado",
    observedOccluded: "oculta",
    observedFailed: "No se pudo cargar el movimiento observado: {detail}",
    simulationConsoleLabel: "LO QUE CORRE LA SIMULACIÓN LOCAL",
    simulationGapLabel: "LO QUE FALTA PARA QUE ESTO MUEVA AL ROBOT",
    simulationGapIntro: "La simulación de la derecha usa una trayectoria interna, no el video. Para que el movimiento del video moviera de verdad al robot falta:",
    simulationGapProfile: "Un perfil ARP-1 importado de este robot exacto, para conocer sus articulaciones, ejes y límites.",
    simulationGapMap: "Un mapa de articulaciones escrito por una persona, de cada articulación observada a una del robot, con signo y convención de cero.",
    simulationGapWhy: "La app no inventa ese mapa: pasar los ángulos de un antebrazo humano a un brazo de seis ejes no es una conversión, es un error de categoría.", nextStepApprovedComputer: "Aprobado. Define un ensayo aislado de navegador para probarlo. El plan lo escribes y lo apruebas tú.",
    nextStepPractice: "Preparar ensayo", nextStepRejected: "El rechazo quedó registrado. Puedes extraer otra vez; sería una nueva llamada de pago.",
    nextStepFailed: "No se extrajo ningún procedimiento. Puedes intentarlo otra vez; sería una nueva llamada de pago.", nextStepRetry: "Extraer otra vez",
    motionTitle: "Vista lateral esquemática del movimiento demostrado",
    motionDescription: "{robot}: {count} waypoints en {duration} s. Los ángulos validados se dibujan como una cadena articulada.",
    motionIdleDescription: "Sin demostración cargada. Ejecuta la simulación local para ver la trayectoria validada.",
    motionLegend: "Proyección esquemática de los ángulos validados. No es simulación física, verificación de colisiones ni control de hardware.",
    motionPlay: "Reproducir el movimiento", motionPause: "Pausar el movimiento", motionScrubberLabel: "Momento de la trayectoria",
    motionPhase: "Fase", motionIdlePhase: "Sin demostración cargada", motionGripper: "Pinza {percent}%", motionNoGripper: "Pinza no declarada",
    motionJump: "Ir a {label} ({time} s)",
    useExample: "Usar un ejemplo", exampleTask: "Enseñar a un brazo robótico a recoger y colocar una pieza frágil sin golpearla.",
    exampleRobot: "APRENDIZ SimArm-6", exampleSource: "https://youtu.be/-fD2TSL2s7I",
    exampleApplied: "Ejemplo cargado. Puedes editar cualquier dato antes de continuar.",
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
    readyStatus: "Simulation complete", sourceTag: "BUILT-IN TRAJECTORY · NOT THE VIDEO", demoTask: "Pick and place a fragile component", builtInTrajectory: "{robot} · built-in demonstration", builtInTrajectoryIdle: "Built-in demonstration trajectory", sourceDetected: "<i></i> Structured trajectory",
    pipelineLabel: "Processing stages", memory: "PROCEDURAL MEMORY", metricLabels: ["Steps", "Rules", "Examples", "Accuracy"], logLabel: "Activity log",
    idleLog: "Waiting for a demonstration to begin…", resultTitle: "Local procedure validated", resultCopy: "The backend extracted and evaluated a safe simulated trajectory.",
    disclosure: "<span aria-hidden=\"true\">i</span> This session calls the real backend and processes a structured local trajectory. It does not call Gemini, interpret the video yet, or control hardware.",
    pending: "PENDING", active: "ACTIVE", complete: "DONE",
    processStages: [["Validating the demonstration", "Checking joints, timing, and velocity"], ["Extracting the motion", "Turning waypoints into steps and rules"], ["Preparing a replay", "Building an execution against the reference"], ["Evaluating the replay", "Comparing position, duration, and safety"], ["Preparing delivery", "Checking the Docker package contract"]],
    processStatuses: ["Validating simulated trajectory", "Building procedural memory", "Preparing reference replay", "Evaluating observable metrics", "Preparing Docker contract"],
    processLogs: ["Session created; validating a six-joint trajectory.", "Limits, timestamps, and velocities checked by the backend.", "Observable procedure extracted from structured waypoints.", "Replay compared with its reference; this is not hardware validation.", "Docker contract prepared; cloud calls made: 0."],
    processError: "The backend could not complete the session. Check its status and try again.",
    trainerEyebrow: "NEW TRAINING", trainerTitle: "What should your<br>agent learn?", trainerIntro: "Define the task, share a demonstration, and review the plan before starting.",
    workspaceLabel: "APRENDIZ / WORKSPACE", workspaceViewLabel: "Workspace view", workspaceViews: ["Teach", "Setup", "Video", "Practice", "Simulation"], workspaceClose: "Close workspace", spendTokenLabel: "Spend token", spendTokenPlaceholder: "Paste the token", spendTokenMissing: "This deployment requires a spend token. Paste it in the top bar before continuing.", spendTokenRejected: "The server rejected the spend token. It has most likely been rotated: paste the current one in the top bar and try again.", httpFailure: "The server answered {status} with no explanation.", approveFailed: "The selection could not be approved: {detail}", projectFailed: "The project could not be prepared: {detail}", processFailedDetail: "The backend could not complete the session: {detail}", networkFailure: "The server could not be reached.", spendRemaining: "{amount} {currency} left", spendTooltip: "Spent {spent} of {ceiling} {currency} in {period}, across {calls} paid call(s).", spendExhausted: "{currency} ceiling reached", spendCeilingReached: "This application reached its spending ceiling. No further calls will be made until you raise it or the month rolls over.", workspaceContexts: { teach: "Teach the agent", setup: "Advanced setup", video: "Video review", practice: "Isolated practice", simulation: "Local simulation" }, procedurePrevious: "Previous step", procedureNext: "Next step",
    formProgressLabel: "Configuration progress", formMarkers: ["Task", "Destination", "Source", "Review"], taskLegend: "Describe the result you need", taskLabel: "Agent task",
    taskPlaceholder: "Example: Teach a robot arm to pick and place a fragile component.", taskHelp: "Describe the outcome and important limits. This first session runs in simulation only.",
    continue: "Continue <span aria-hidden=\"true\">→</span>", destinationLegend: "Where will the learned behavior run?", destinationTypeLabel: "Execution destination",
    robot: "Robot", robotCopy: "Motion validated in simulation first", computer: "Computer", computerCopy: "Procedure isolated before execution",
    robotModelLabel: "Exact brand and model", robotModelPlaceholder: "Example: Unitree Go2", robotHelp: "We will use ARP-1 and select a compatible simulator automatically.",
    computerAppLabel: "Target application", computerAppPlaceholder: "Example: Google Chrome, Excel, or Blender", computerHelp: "The operating system will be detected automatically and the first run will be isolated.",
    sourceLegend: "Add a reference for the future demonstration", sourceTypeLabel: "Source type", youtubeCopy: "Instructional video reference",
    upload: "Local video", uploadCopy: "Kept on this machine, never sent", automatic: "Automatic search", automaticCopy: "Find references for you to approve", videoUrlLabel: "Reference link", selectVideo: "Select a video", fileTypes: "MP4, MOV, WEBM, or MKV",
    uploadNote: "The file is kept on this machine and is never sent to a cloud model. A procedure cannot be extracted from a local file yet: that still needs a public YouTube URL.",
    uploadStore: "Keep on this machine",
    uploadStoring: "Keeping…",
    uploadNeedsProject: "Create the project before keeping a video.",
    uploadRemove: "Remove",
    uploadMeta: "{size} · sha256 {hash} · not sent",
    uploadFailed: "The video could not be kept: {detail}",
    historyLabel: "VERSION HISTORY",
    historyTotals: "{versions} versions \u00b7 {calls} cloud calls \u00b7 {tokens} tokens",
    historyVersion: "V{version}",
    historyVersionMeta: "{steps} steps \u00b7 {status}",
    historyDiffLabel: "V{from} \u2192 V{to}",
    historyNoChanges: "No difference between these two versions.",
    historyDiffSummary: "{changed} changed \u00b7 {added} added \u00b7 {removed} removed \u00b7 {unchanged} identical.",
    historySameSource: "Both versions came from the same video.",
    historyCrossSource: "These versions came from different videos.",
    historyStepChanged: "Step {step}:",
    historyStepAdded: "Step {step} added: {after}",
    historyStepRemoved: "Step {step} removed: {before}",
    historyListAdded: "{field} added: {value}",
    historyListRemoved: "{field} removed: {value}",
    reconciliationLabel: "RECONCILIATION",
    reconciliationSummary: "{sources} approved sources \u00b7 {distinct} distinct videos \u00b7 confidence {confidence} \u00b7 {conflicts} contradictions.",
    reconciliationNone: "Approve a second extraction before this can reconcile.",
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
    adaptationSummary: "{actionable} of {total} steps could run at this destination.",
    adaptationMissing: "Missing: {missing}", adaptationBlocked: "Nothing runs without your explicit approval.",
    motionLabel: "MOTION EVIDENCE",
    motionIntro: "Prose steps never become a trajectory. This analysis samples {fps} fps across {window} s of the video you already approved and returns timestamped joint angles.",
    motionAck: "I understand this spends one cloud call on the source you already approved.",
    motionRun: "Analyze motion (1 call)",
    motionRunning: "Analyzing motion…",
    motionVerdictUsable: "Samples are usable",
    motionVerdictSuspect: "Samples are suspect",
    motionVerdictNotEvidence: "This is not evidence",
    motionStats: "{samples} samples · {joints} joints · {span} s observed · {rate} samples/s · mean confidence {confidence} · {tokens} tokens · {elapsed} s",
    motionEstimate: "Angles estimated by a vision model, not measured.",
    motionFinding: {
      no_samples: "The analysis returned no usable joint samples.",
      mirrored_sides: "Left and right carry exactly the same angle in {identical} of {paired} paired readings. Two limbs of a walking body do not move identically, so these sides are not independent observations.",
      uniform_confidence: "All {samples} samples report the identical confidence {confidence}, so confidence distinguishes nothing and was not estimated per sample.",
      uniform_visibility: "All {samples} samples report the identical visibility “{visibility}”, so occlusion was not judged frame by frame.",
      acyclic_all: "Every measured joint ({joints}) traces a single rise and fall across the whole {window}s window. Walking repeats about once a second, so one arc is a drawn curve rather than a measured gait cycle.",
      acyclic_some: "{flagged} of {checked} joints ({joints}) swing widely but reverse at most once across the window.",
    },
    motionFailed: "Motion analysis failed: {detail}",
    motionBudget: "Request refused before spending: {detail}",
    recentWorkLabel: "SAVED WORK", recentWorkNote: "Stored on this machine. Open one to continue where you left off.",
    recentWorkOpen: "Open {task}", recentWorkRobot: "Robot", recentWorkComputer: "Computer",
    recentWorkApproved: "Procedure approved", recentWorkRejected: "Procedure rejected", recentWorkAwaiting: "Awaiting review",
    recentWorkFailed: "Extraction failed", recentWorkNoExtraction: "No extraction", recentWorkOpened: "Project {id} restored from local storage.",
    extractionActivityNote: "One bounded Vertex call is still running. Keep this view open.",
    nextStepLabel: "NEXT STEP", nextStepAwaitingReview: "Read the steps, then approve or reject the procedure.",
    nextStepApprovedRobot: "Approved. Now validate the motion in the local simulation. That simulation uses a built-in trajectory, not the video.",
    nextStepSimulate: "Validate in simulation",
    teachEyebrow: "TEACH THE AGENT",
    teachTitle: "Say what it should learn, and from which video.",
    teachTaskLabel: "What should it learn?",
    teachTaskPlaceholder: "Example: How a human arm works, so a robot can learn it.", teachTargetPlaceholderRobot: "Example: APRENDIZ SimArm-6", teachTargetPlaceholderComputer: "Example: Google Chrome",
    teachUrlLabel: "Video link (YouTube)",
    teachUrlPlaceholder: "https://youtube.com/…",
    teachDestinationLabel: "Where will it run?",
    teachRobot: "Robot", teachRobotHelp: "Validated in local simulation.",
    teachComputer: "Computer", teachComputerHelp: "Isolated rehearsal in a browser.",
    teachTargetRobot: "Exact robot model", teachTargetComputer: "Application on the computer", teachTargetError: "Name the exact robot model or the application (at least 2 characters).",
    teachConsent: "I authorise up to {calls} paid Vertex call(s) for this learning. {remaining} left.",
    teachConsentNoCeiling: "I authorise up to {calls} paid Vertex call(s) for this learning.",
    teachAdvanced: "Advanced setup", teachStart: "Teach the agent",
    teachTaskError: "Describe the task in at least 12 characters.",
    teachUrlError: "Paste a valid link that starts with http.",
    teachConsentError: "Tick the authorisation before continuing.",
    teachProgressLabel: "THE AGENT IS WORKING",
    teachStages: {
      project: ["Prepare the project", "Records the task and the destination"],
      extract: ["Extract the procedure from the video", "One bounded Vertex call"],
      review: ["Your approval", "Nothing is adapted or executed without it"],
      adapt: ["Adapt to the destination", "What could run and what is missing"],
      motion: ["Analyse the motion", "One bounded Vertex call"],
      ready: ["Ready", "Your agent is ready to download"],
    },
    teachStates: { pending: "Pending", running: "Running", waiting: "Waiting for you", done: "Done", failed: "Failed" },
    teachRetry: "Back to the form",
    teachApprovalLabel: "THIS IS WHAT IT LEARNED — DO YOU APPROVE?",
    teachReject: "Reject", teachApprove: "Approve",
    teachRejected: "You rejected the procedure. You can teach again; that would be another paid call.",
    teachReviewError: "Your decision could not be recorded.",
    teachResultEyebrow: "YOUR AGENT",
    teachNoPlan: "No adaptation plan is available.",
    teachMotionFailed: "The motion analysis did not complete: {detail} The agent can still be downloaded, without that evidence.",
    teachViewDetail: "See detail", teachViewSimulation: "Simulation", teachDownload: "Download agent",
    teachDownloading: "Preparing the package…",
    teachDownloadNote: "A self-contained Docker package. Anyone with Docker starts it with start.sh or start.ps1; nothing else is needed.",
    teachDownloaded: "Downloaded {name} ({files} files). Unzip it and run start.sh or start.ps1.",
    simulationEyebrow: "LOCAL SIMULATION",
    simulationTitle: "What the video taught, and what this simulation actually runs.",
    simulationLearnedLabel: "WHAT THE VIDEO TAUGHT",
    simulationLearnedNote: "{count} steps extracted from the source you approved, each with the video timestamp it came from.",
    simulationLearnedEmpty: "There is no approved procedure for this session yet.",
    simulationMotionLabel: "OBSERVED MOTION",
    simulationMotionNone: "You have not analysed the video's motion yet. That analysis lives in the Video view and spends one call.",
    simulationMotionSummary: "{subject} · {chain} chain · {samples} samples of {joints} joints across {span} s · mean confidence {confidence}.",
    observedTag: "FROM THE VIDEO · ESTIMATED ANGLES",
    observedTagRejected: "FROM THE VIDEO · SAMPLES REJECTED",
    observedTagSuspect: "FROM THE VIDEO · SAMPLES SUSPECT",
    observedTitle: "Joint angles observed in the video",
    observedDescription: "{joints} observed joints across {duration} s, each drawn as its own angle over time.",
    observedSummary: "This one does come from your video: {joints} joints, {duration} s, {points} readings. Each line is an angle, not a body.",
    observedSummaryUnverified: "{joints} joints, {duration} s, {points} readings returned by the model. Each line is an angle, not a body.",
    observedVerdictNotEvidence: "The arithmetic audit rejected these samples: they are not observations. What is drawn below is what the model returned, not what the body in the video did. The reasons are in the Video view.",
    observedVerdictSuspect: "The audit marked these samples as suspect. Read them as the model's draft, not as measurement. The reasons are in the Video view.",
    observedOmitted: " {count} joints that moved less were left out.",
    observedLegend: "Angles estimated by a vision model, not measured. A line breaks where the joint stopped being visible, and that gap is not filled in. The body is not reconstructed, because the samples never say where each part is or how long it is.",
    observedPlay: "Play the observed motion",
    observedPause: "Pause the observed motion",
    observedScrubberLabel: "Observed motion time",
    observedOccluded: "occluded",
    observedFailed: "The observed motion could not be loaded: {detail}",
    simulationConsoleLabel: "WHAT THE LOCAL SIMULATION RUNS",
    simulationGapLabel: "WHAT IS MISSING BEFORE THIS COULD DRIVE THE ROBOT",
    simulationGapIntro: "The simulation on the right runs a built-in trajectory, not the video. For the video's motion to actually drive the robot, this is missing:",
    simulationGapProfile: "An imported ARP-1 profile for this exact robot, so its joints, axes, and limits are known.",
    simulationGapMap: "A human-authored joint map from each observed joint to a robot joint, including sign and zero convention.",
    simulationGapWhy: "The application will not invent that map: sending a human forearm's angles to a six-axis arm is not a conversion, it is a category error.", nextStepApprovedComputer: "Approved. Define an isolated browser rehearsal to test it. You write and approve that plan yourself.",
    nextStepPractice: "Set up rehearsal", nextStepRejected: "The rejection is recorded. You can extract again; that would be another paid call.",
    nextStepFailed: "No procedure was extracted. You can try again; that would be another paid call.", nextStepRetry: "Extract again",
    motionTitle: "Schematic side view of the demonstrated motion",
    motionDescription: "{robot}: {count} waypoints across {duration} s. Validated angles are drawn as an articulated chain.",
    motionIdleDescription: "No demonstration loaded. Run the local simulation to see the validated trajectory.",
    motionLegend: "Schematic projection of validated joint angles. Not a physics simulation, a collision check, or hardware control.",
    motionPlay: "Play the motion", motionPause: "Pause the motion", motionScrubberLabel: "Trajectory time",
    motionPhase: "Phase", motionIdlePhase: "No demonstration loaded", motionGripper: "Gripper {percent}%", motionNoGripper: "Gripper not declared",
    motionJump: "Jump to {label} ({time} s)",
    useExample: "Use an example", exampleTask: "Teach a robot arm to pick and place a fragile component without knocking it over.",
    exampleRobot: "APRENDIZ SimArm-6", exampleSource: "https://youtu.be/-fD2TSL2s7I",
    exampleApplied: "Example loaded. You can edit any value before continuing.",
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
const motionError = document.querySelector("#motion-error");
const videoProcedureEvidence = document.querySelector("#video-procedure-evidence");
const procedureReview = document.querySelector("#procedure-review");
const approveVideoProcedureButton = document.querySelector("#approve-video-procedure");
const rejectVideoProcedureButton = document.querySelector("#reject-video-procedure");
const workspace = document.querySelector("#entrenar");
const workspaceCloseButton = document.querySelector("#workspace-close");
const teachForm = document.querySelector("#teach-form");
const teachTask = document.querySelector("#teach-task");
const teachUrl = document.querySelector("#teach-url");
const teachTarget = document.querySelector("#teach-target");
const teachTargetLabel = document.querySelector("#teach-target-label");
const teachConsent = document.querySelector("#teach-consent");
const teachConsentText = document.querySelector("#teach-consent-text");
const teachError = document.querySelector("#teach-error");
const teachStart = document.querySelector("#teach-start");
const teachAdvanced = document.querySelector("#teach-advanced");
const teachProgress = document.querySelector("#teach-progress");
const teachStagesList = document.querySelector("#teach-stages");
const teachProgressError = document.querySelector("#teach-progress-error");
const teachRetry = document.querySelector("#teach-retry");
const teachApproval = document.querySelector("#teach-approval");
const teachApprove = document.querySelector("#teach-approve");
const teachReject = document.querySelector("#teach-reject");
const teachResult = document.querySelector("#teach-result");
const teachResultError = document.querySelector("#teach-result-error");
const teachViewDetail = document.querySelector("#teach-view-detail");
const teachViewSimulation = document.querySelector("#teach-view-simulation");
const teachDownload = document.querySelector("#teach-download");
const teachDownloadNote = document.querySelector("#teach-download-note");
const teachDestinationInputs = [...document.querySelectorAll('input[name="teach-destination"]')];
const simulationPanel = document.querySelector("#workspace-simulation");
const simulationConsoleHost = document.querySelector("#simulation-console-host");
const observedPanel = document.querySelector("#observed-motion");
const observedCanvas = document.querySelector("#observed-canvas");
const observedPlayButton = document.querySelector("#observed-play");
const observedScrubber = document.querySelector("#observed-scrubber");
const processingSectionHome = document.querySelector("#procesamiento");
const spendTokenField = document.querySelector("#spend-token-field");
const spendRemainingLabel = document.querySelector("#spend-remaining");
const spendTokenInput = document.querySelector("#spend-token");
const workspaceViewButtons = [...document.querySelectorAll("[data-workspace-target]")];
const procedureStepPager = document.querySelector("#procedure-step-pager");
const procedureStepPrevious = document.querySelector("#procedure-step-previous");
const procedureStepNext = document.querySelector("#procedure-step-next");
const motionCanvas = document.querySelector("#motion-canvas");
const motionPlayButton = document.querySelector("#motion-play");
const motionScrubber = document.querySelector("#motion-scrubber");
const motionTicks = document.querySelector("#motion-ticks");
const useExampleButton = document.querySelector("#use-example");
const recentWork = document.querySelector("#recent-work");
const recentWorkList = document.querySelector("#recent-work-list");
const extractionActivity = document.querySelector("#extraction-activity");
const videoNextStep = document.querySelector("#video-next-step");
const motionEvidence = document.querySelector("#motion-evidence");
const storeVideoFileButton = document.querySelector("#store-video-file");
const uploadList = document.querySelector("#upload-list");
const uploadError = document.querySelector("#upload-error");
const evidenceHistory = document.querySelector("#evidence-history");
const historyVersions = document.querySelector("#history-versions");
const historyDiff = document.querySelector("#history-diff");
const historyChanges = document.querySelector("#history-changes");
const historyReconciliation = document.querySelector("#history-reconciliation");
const reconciliationConflicts = document.querySelector("#reconciliation-conflicts");
const motionCostApproval = document.querySelector("#motion-cost-approval");
const runMotionAnalysisButton = document.querySelector("#run-motion-analysis");
const motionResult = document.querySelector("#motion-result");
const motionFindings = document.querySelector("#motion-findings");
const videoNextStepAction = document.querySelector("#video-next-step-action");
const stepJumpButtons = [...document.querySelectorAll("[data-step-jump]")];
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
let currentProcedureStep = 0;
let workspaceReturnFocus = null;
let motionPreview = null;
let motionPreviewKey = null;
let motionScene = null;
let motionTime = 0;
let motionPlaying = false;
let motionIntent = false;
let motionOnScreen = true;
let motionFrameId = 0;
let motionLastTimestamp = 0;
let extractionTimerId = 0;
let videoNextStepHandler = null;
let motionAnalysis = null;
let observedPreview = null;
let observedPreviewKey = null;
let observedScene = null;
let observedTime = 0;
let observedIntent = false;
let observedPlaying = false;
let observedFrameId = 0;
let observedLastTimestamp = 0;
let storedUploads = [];
let procedureHistory = null;
let projectReconciliation = null;
let uploadRunning = false;
let motionAnalysisRunning = false;
const MOTION_FPS = 4;
const MOTION_WINDOW_SECONDS = 12;
let storedProjects = [];
let adaptationPlan = null;
// The Teach view drives the same machinery the detailed views expose; these
// hold only what it needs to show its own progress.
let teachRunning = false;
let teachStages = [];
let teachStatus = {};
let teachDestinationValue = "robot";
let teachStageStartedAt = 0;
let teachTicker = null;
let lastSpendState = null;

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
  setContent("#trainer-intro-copy", t.trainerIntro);
  setContent("#workspace-label", t.workspaceLabel);
  document.querySelector(".workspace-switcher").ariaLabel = t.workspaceViewLabel;
  workspaceViewButtons.forEach((button, index) => { button.textContent = t.workspaceViews[index]; });
  workspaceCloseButton.ariaLabel = t.workspaceClose;
  setContent("#spend-token-label", t.spendTokenLabel);
  renderSimulationEvidence();
  renderTeachLabels();
  spendTokenInput.placeholder = t.spendTokenPlaceholder;
  procedureStepPrevious.ariaLabel = t.procedurePrevious;
  procedureStepNext.ariaLabel = t.procedureNext;
  document.querySelector(".step-nav").ariaLabel = t.formProgressLabel;
  markers.forEach((marker, index) => { marker.querySelector("button").innerHTML = `<span>0${index + 1}</span> ${t.formMarkers[index]}`; });
  setContent('[data-step="1"] legend', t.taskLegend);
  setContent('label[for="task-description"]', t.taskLabel);
  taskInput.placeholder = t.taskPlaceholder;
  setContent(".field-help", t.taskHelp);
  setContent("#use-example", t.useExample);
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
  renderUploads();
  renderEvidenceHistory();
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
  renderRecentWork();
  renderMotionLabels();
  drawMotionFrame(motionTime);
  setWorkspaceView(workspace.dataset.workspaceView || "setup", false);
  if (currentProject && videoProcedureRecord?.status === "approved") {
    void loadAdaptationPlan();
  }
}

function showStep(stepNumber) {
  currentStep = stepNumber;
  steps.forEach((step) => { const active = Number(step.dataset.step) === stepNumber; step.hidden = !active; step.classList.toggle("is-active", active); });
  markers.forEach((marker) => { const markerStep = Number(marker.dataset.stepMarker); marker.classList.toggle("is-active", markerStep === stepNumber); marker.classList.toggle("is-complete", markerStep < stepNumber); });
  stepJumpButtons.forEach((button) => { button.disabled = Number(button.dataset.stepJump) >= stepNumber; });
  steps.find((step) => Number(step.dataset.step) === stepNumber)?.querySelector("textarea, input:not([type='radio']), button")?.focus({ preventScroll: true });
}

function setWorkspaceView(view, moveFocus = true) {
  if (!["teach", "setup", "video", "practice", "simulation"].includes(view)) return;
  const viewButton = workspaceViewButtons.find((button) => button.dataset.workspaceTarget === view);
  if (viewButton?.hidden) return;
  if (view === "simulation") {
    simulationPanel.hidden = false;
    mountSimulationConsole();
    renderSimulationEvidence();
  }
  workspace.dataset.workspaceView = view;
  syncObservedPlayback();
  workspaceViewButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.workspaceTarget === view)));
  setContent("#workspace-context", translations[currentLanguage].workspaceContexts[view]);
  if (!moveFocus) return;
  const focusTarget = view === "setup"
    ? steps.find((step) => !step.hidden)?.querySelector("textarea, input:not([type='radio']), button")
    : view === "video"
      ? (procedureReview.hidden ? extractVideoButton : procedureStepNext)
      : view === "simulation"
        ? simulationPanel
        : view === "teach"
          ? teachTask
          : browserTargetUrl;
  requestAnimationFrame(() => focusTarget?.focus({ preventScroll: true }));
}

function openWorkspace(view = "setup", trigger = document.activeElement) {
  workspaceReturnFocus = trigger instanceof HTMLElement ? trigger : null;
  document.body.classList.add("workspace-open");
  workspace.setAttribute("aria-hidden", "false");
  setWorkspaceView(view);
  syncMotionPlayback();
  history.replaceState(null, "", `${location.pathname}${location.search}#entrenar`);
}

function closeWorkspace() {
  releaseSimulationConsole();
  setObservedPlaying(false);
  document.body.classList.remove("workspace-open");
  workspace.setAttribute("aria-hidden", "true");
  history.replaceState(null, "", `${location.pathname}${location.search}`);
  syncMotionPlayback();
  workspaceReturnFocus?.focus({ preventScroll: true });
}

function trapWorkspaceFocus(event) {
  if (event.key !== "Tab" || !document.body.classList.contains("workspace-open")) return;
  const focusable = [...workspace.querySelectorAll("a[href], button:not(:disabled), input:not(:disabled), textarea:not(:disabled), summary")]
    .filter((element) => !element.hidden && element.offsetParent !== null);
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
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
  setButtonBusy(approveSourcesButton, false);
  setContent("#approve-sources", t.approveSources);
}

async function searchAutomaticSources() {
  const t = translations[currentLanguage];
  const query = sourceQuery.value.trim();
  if (query.length < 3) {
    renderSourceStatus(t.automaticError, true);
    return;
  }
  if (missingSpendToken()) {
    renderSourceStatus(t.spendTokenMissing, true);
    spendTokenInput.focus({ preventScroll: true });
    return;
  }
  approvedSources = [];
  sourceSearch = null;
  searchSourcesButton.disabled = true;
  setButtonBusy(searchSourcesButton, true);
  approveSourcesButton.hidden = true;
  setContent("#search-sources", t.searching);
  renderSourceStatus(t.searching);
  try {
    const response = await fetch("/api/sources/search", {
      method: "POST",
      headers: spendHeaders(),
      body: JSON.stringify({
        query,
        language: currentLanguage,
        max_results: 3,
        acknowledge_search_quota: true,
      }),
    });
    if (!response.ok) throw new Error(failureDetail(response, await response.json().catch(() => null)));
    sourceSearch = await response.json();
    renderSourceCandidates(sourceSearch.candidates);
  } catch (error) {
    // The reason was already worked out; "unavailable" would throw it away.
    renderSourceStatus(error?.message || t.searchUnavailable, true);
    console.error(error);
  } finally {
    searchSourcesButton.disabled = false;
    setButtonBusy(searchSourcesButton, false);
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
  setButtonBusy(approveSourcesButton, true);
  setContent("#approve-sources", t.approving);
  try {
    const response = await fetch(`/api/sources/search/${encodeURIComponent(sourceSearch.search_id)}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_ids: selectedIds }),
    });
    if (!response.ok) {
      throw new Error(failureDetail(response, await response.json().catch(() => null)));
    }
    const result = await response.json();
    approvedSources = result.approved_sources;
    renderSourceStatus(t.sourceApproved.replace("{count}", String(approvedSources.length)));
    approveSourcesButton.hidden = true;
    sourceError.textContent = "";
  } catch (error) {
    // Approving is not searching; reporting the search as unconfigured sent
    // people to fix something that was never the problem.
    renderSourceStatus(t.approveFailed.replace("{detail}", thrownDetail(error)), true);
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

// A deployment that configures SPEND_TOKEN refuses every paid endpoint that
// arrives without the header, and the console cannot guess the value. It is
// the operator's credential, so it is held in sessionStorage: long enough to
// survive a reload while the tab is open, gone when the tab closes. That is
// as long as a shared secret pasted into a browser should live anywhere.
const SPEND_TOKEN_KEY = "aprendiz-spend-token";
let spendTokenRequired = false;

function storedSpendToken() {
  const typed = spendTokenInput?.value.trim();
  if (typed) return typed;
  try { return sessionStorage.getItem(SPEND_TOKEN_KEY) || ""; } catch (_) { return ""; }
}

function rememberSpendToken() {
  const token = spendTokenInput.value.trim();
  spendTokenField.classList.toggle("is-set", Boolean(token));
  try {
    if (token) sessionStorage.setItem(SPEND_TOKEN_KEY, token);
    else sessionStorage.removeItem(SPEND_TOKEN_KEY);
  } catch (_) { /* Keep the token in the field for this page only. */ }
}

function spendHeaders() {
  const headers = { "Content-Type": "application/json" };
  const token = storedSpendToken();
  if (token) headers["X-Aprendiz-Spend-Token"] = token;
  return headers;
}

// Refuse locally rather than send a request that is already known to fail.
function missingSpendToken() {
  return spendTokenRequired && !storedSpendToken();
}

// The ceiling is enforced on the server; this only shows what is left of it,
// so a person can see a run getting expensive before a refusal explains it.
function renderSpendRemaining(spend) {
  lastSpendState = spend || null;
  renderTeachConsent();
  if (!spendRemainingLabel) return;
  if (!spend?.enforced) { spendRemainingLabel.hidden = true; return; }
  const t = translations[currentLanguage];
  const remaining = Number(spend.remaining ?? 0);
  const exhausted = remaining <= 0;
  spendRemainingLabel.hidden = false;
  spendRemainingLabel.textContent = exhausted
    ? t.spendExhausted.replace("{currency}", spend.currency)
    : t.spendRemaining
        .replace("{amount}", spendFigure(remaining, Number(spend.ceiling ?? 0), Number(spend.spent ?? 0)))
        .replace("{currency}", spend.currency);
  // The exact figures, for anyone who wants to check the rounding.
  spendRemainingLabel.title = t.spendTooltip
    .replace("{spent}", String(spend.spent))
    .replace("{ceiling}", String(spend.ceiling))
    .replace("{currency}", spend.currency)
    .replace("{period}", spend.period)
    .replace("{calls}", String(spend.calls));
  spendRemainingLabel.classList.toggle("is-spent", exhausted);
  spendRemainingLabel.classList.toggle(
    "is-low",
    !exhausted && spend.ceiling > 0 && remaining / spend.ceiling <= 0.2,
  );
}

/* Two decimals hid every real call: a 20.00 ceiling with 0.004 spent still
   printed "20.00 left", which reads as a ceiling doing nothing. Show only as
   many decimals as it takes for spending to be visible at all. */
function spendFigure(remaining, ceiling, spent) {
  if (spent > 0 && remaining.toFixed(2) === ceiling.toFixed(2)) {
    for (const digits of [3, 4, 5, 6]) {
      if (remaining.toFixed(digits) !== ceiling.toFixed(digits)) {
        return remaining.toFixed(digits);
      }
    }
  }
  return remaining.toFixed(2);
}

// Read after anything that may have spent, so the number is not stale.
async function refreshSpendState() {
  try {
    const response = await fetch("/api/status");
    if (response.ok) renderSpendRemaining((await response.json()).spend);
  } catch (_) { /* Leave the last known figure showing. */ }
}

/* A rotated secret is the ordinary reason a paid call starts refusing, and a
   stored copy of the old one is then worse than nothing: the field looks
   configured, so nobody suspects it. A 401 drops it and says so. */
function forgetRejectedSpendToken() {
  try { sessionStorage.removeItem(SPEND_TOKEN_KEY); } catch (_) { /* Field only. */ }
  spendTokenInput.value = "";
  spendTokenField.classList.remove("is-set");
  spendTokenField.hidden = false;
  spendTokenInput.focus({ preventScroll: true });
}

/* Never returns an empty string. "Motion analysis failed:" with nothing after
   the colon tells a reader only that something is wrong, which is exactly
   where a rotated token used to leave them. */
function failureDetail(response, body) {
  const t = translations[currentLanguage];
  if (response.status === 401) {
    forgetRejectedSpendToken();
    return t.spendTokenRejected;
  }
  if (response.status === 402) return t.spendCeilingReached;
  const detail = body?.detail;
  if (typeof detail === "string" && detail) return detail;
  if (detail?.violations?.length) return detail.violations.join(" ");
  return t.httpFailure.replace("{status}", String(response.status));
}

function thrownDetail(error) {
  return error?.message || translations[currentLanguage].networkFailure;
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
  procedure.steps.forEach((step, index) => {
    const item = document.createElement("li");
    item.hidden = index !== 0;
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
  currentProcedureStep = 0;
  renderProcedureStepPage();
  renderProcedureList("#procedure-rules", procedure.rules);
  renderProcedureList("#procedure-exceptions", procedure.exceptions);
  renderProcedureList("#procedure-examples", procedure.examples);
  renderProcedureList("#procedure-uncertainties", procedure.uncertainties);
}

function renderProcedureStepPage() {
  const items = [...document.querySelector("#procedure-steps").children];
  if (!items.length) {
    procedureStepPager.hidden = true;
    return;
  }
  currentProcedureStep = Math.max(0, Math.min(currentProcedureStep, items.length - 1));
  items.forEach((item, index) => { item.hidden = index !== currentProcedureStep; });
  procedureStepPager.hidden = items.length <= 1;
  setContent("#procedure-step-position", `${currentProcedureStep + 1} / ${items.length}`);
  procedureStepPrevious.disabled = currentProcedureStep === 0;
  procedureStepNext.disabled = currentProcedureStep === items.length - 1;
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

function setButtonBusy(button, busy) {
  if (!button) return;
  button.classList.toggle("is-busy", busy);
  if (busy) button.setAttribute("aria-busy", "true");
  else button.removeAttribute("aria-busy");
}

function startExtractionTimer() {
  const startedAt = performance.now();
  window.clearInterval(extractionTimerId);
  setContent("#extraction-elapsed", "0.0 s");
  extractionTimerId = window.setInterval(() => {
    setContent("#extraction-elapsed", `${((performance.now() - startedAt) / 1000).toFixed(1)} s`);
  }, 100);
}

function stopExtractionTimer() {
  window.clearInterval(extractionTimerId);
  extractionTimerId = 0;
}

/* The console is one node carrying one set of ids, and app.js addresses all of
   them. So it is moved into the workspace rather than copied: a duplicate
   would give every id two owners and silently break every binding. */
function mountSimulationConsole() {
  if (!processingConsole || !simulationConsoleHost) return;
  if (processingConsole.parentElement !== simulationConsoleHost) {
    simulationConsoleHost.append(processingConsole);
  }
}

function releaseSimulationConsole() {
  if (!processingConsole || !processingSectionHome) return;
  if (processingConsole.parentElement === simulationConsoleHost) {
    processingSectionHome.insertBefore(
      processingConsole,
      processingSectionHome.querySelector(".demo-disclosure"),
    );
  }
}

function consoleIsInWorkspace() {
  return processingConsole?.parentElement === simulationConsoleHost;
}

/* Two columns that must not be read as one. The left is what the video taught;
   the right is a built-in trajectory. The gap between them is stated rather
   than left for someone to assume away. */
function renderSimulationEvidence() {
  if (!simulationPanel) return;
  const t = translations[currentLanguage];
  setContent("#simulation-eyebrow", t.simulationEyebrow);
  setContent("#simulation-title", t.simulationTitle);
  setContent("#simulation-learned-label", t.simulationLearnedLabel);
  setContent("#simulation-motion-label", t.simulationMotionLabel);
  setContent("#simulation-console-label", t.simulationConsoleLabel);
  setContent("#simulation-gap-label", t.simulationGapLabel);
  setContent("#simulation-gap-intro", t.simulationGapIntro);

  const steps = videoProcedureRecord?.procedure?.steps || [];
  setContent(
    "#simulation-learned-note",
    steps.length
      ? t.simulationLearnedNote.replace("{count}", String(steps.length))
      : t.simulationLearnedEmpty,
  );

  const list = document.querySelector("#simulation-steps");
  list.replaceChildren();
  steps.forEach((step) => {
    const item = document.createElement("li");
    const stamps = (step.source_timestamps || []).join(" · ");
    if (stamps) {
      const time = document.createElement("time");
      time.textContent = stamps;
      item.append(time);
    }
    const action = document.createElement("b");
    action.textContent = step.action;
    item.append(action);
    if (step.evidence) {
      const evidence = document.createElement("span");
      evidence.textContent = step.evidence;
      item.append(evidence);
    }
    list.append(item);
  });

  setContent(
    "#simulation-motion-note",
    motionAnalysis
      ? t.simulationMotionSummary
          .replace("{subject}", motionAnalysis.subject_kind)
          .replace("{chain}", motionAnalysis.kinematic_chain)
          .replace("{samples}", String(motionAnalysis.sample_count))
          .replace("{joints}", String(motionAnalysis.distinct_joint_count))
          .replace("{span}", motionAnalysis.observed_span_seconds.toFixed(1))
          .replace("{confidence}", motionAnalysis.mean_confidence.toFixed(2))
      : t.simulationMotionNone,
  );

  const gap = document.querySelector("#simulation-gap-list");
  gap.replaceChildren();
  [t.simulationGapProfile, t.simulationGapMap, t.simulationGapWhy].forEach((text) => {
    const item = document.createElement("li");
    item.textContent = text;
    gap.append(item);
  });

  renderObservedMotion();
  loadObservedMotionPreview();
}

/* --- The movement that actually came from the video ---------------------
   The console on the right runs a built-in arm, and that is the honest
   answer to "simulate this". It is not the honest answer to "show me my
   video", so this panel answers that question separately, from the samples
   the analysis paid for.

   What it draws is one timeline per joint, and deliberately not a figure.
   The samples carry angles and nothing else -- no link lengths, no joint
   positions, no statement of what connects to what -- so a silhouette drawn
   from them would be geometry this application invented and then displayed
   as evidence. A line here also stops wherever the joint stopped being
   visible: bridging that gap would draw a movement nobody observed. */

/* The joint name and its live angle both sit in the left column, so a narrow
   workspace can scroll the plot without scrolling away what it is a plot of. */
const OBSERVED_VIEW = {
  width: 320,
  labelWidth: 104,
  labelRight: 70,
  valueRight: 98,
  rightGutter: 10,
  rowHeight: 34,
  topPad: 12,
  bottomPad: 20,
};

function observedPlotLeft() {
  return OBSERVED_VIEW.labelWidth;
}

function observedPlotRight() {
  return OBSERVED_VIEW.width - OBSERVED_VIEW.rightGutter;
}

function observedPreviewUrl() {
  return `${motionAnalysisUrl()}/preview`;
}

/* Reshaping samples costs nothing, but fetching them twice for the same
   analysis is still noise: the key is what makes this run once. */
async function loadObservedMotionPreview() {
  const key = motionAnalysis?.analysis_id || null;
  if (!key) {
    observedPreview = null;
    observedPreviewKey = null;
    renderObservedMotion();
    return;
  }
  if (key === observedPreviewKey) return;
  try {
    const response = await fetch(observedPreviewUrl());
    if (!response.ok) return;
    observedPreview = await response.json();
    observedPreviewKey = key;
    observedTime = 0;
    buildObservedScene();
    renderObservedMotion();
    setObservedPlaying(!reducedMotion.matches);
  } catch (error) {
    console.error(error);
  }
}

function observedScale(tracks) {
  const largest = tracks.reduce(
    (top, track) =>
      Math.max(top, Math.abs(track.minimum_degrees), Math.abs(track.maximum_degrees)),
    0,
  );
  return largest > 0 ? largest : 1;
}

/* Split one joint's points wherever the analysis said the stroke breaks. A
   segment is a run the joint was seen through; the space between two of them
   is time nobody watched, and it stays empty. */
function observedSegments(points) {
  const segments = [];
  points.forEach((point) => {
    if (point.starts_segment || !segments.length) segments.push([]);
    segments[segments.length - 1].push(point);
  });
  return segments;
}

function buildObservedScene() {
  observedScene = null;
  if (!observedCanvas) return;
  observedCanvas.textContent = "";
  const preview = observedPreview;
  if (!preview || !preview.tracks.length) return;

  const rowCount = preview.tracks.length;
  const height =
    OBSERVED_VIEW.topPad + rowCount * OBSERVED_VIEW.rowHeight + OBSERVED_VIEW.bottomPad;
  observedCanvas.setAttribute("viewBox", `0 0 ${OBSERVED_VIEW.width} ${height}`);

  const title = svgElement("title", { id: "observed-canvas-title" });
  const description = svgElement("desc", { id: "observed-canvas-desc" });
  observedCanvas.append(title, description);

  const left = observedPlotLeft();
  const right = observedPlotRight();
  const span = preview.duration_seconds;
  const scale = observedScale(preview.tracks);
  const half = OBSERVED_VIEW.rowHeight / 2 - 3;
  const at = (seconds) =>
    span > 0
      ? left + ((seconds - preview.span_start_seconds) / span) * (right - left)
      : left;

  const rows = preview.tracks.map((track, index) => {
    const midY = OBSERVED_VIEW.topPad + index * OBSERVED_VIEW.rowHeight + OBSERVED_VIEW.rowHeight / 2;
    const group = svgElement("g", { class: "observed-row" });

    group.append(
      svgElement("line", {
        class: "observed-baseline",
        x1: left,
        y1: midY,
        x2: right,
        y2: midY,
      }),
    );

    const label = svgElement("text", {
      class: "observed-label",
      x: OBSERVED_VIEW.labelRight,
      y: midY + 3,
      "text-anchor": "end",
    });
    label.textContent = track.label;
    const labelTitle = svgElement("title");
    labelTitle.textContent = `${track.label}: ${Math.round(track.minimum_degrees)}° … ${Math.round(track.maximum_degrees)}°`;
    label.append(labelTitle);
    group.append(label);

    const plotted = track.points.map((point) => ({
      ...point,
      x: at(point.timestamp_seconds),
      y: midY - (point.angle_degrees / scale) * half,
    }));

    observedSegments(plotted).forEach((segment) => {
      if (segment.length < 2) {
        const only = segment[0];
        group.append(
          svgElement("circle", {
            class: "observed-lone-point",
            cx: only.x.toFixed(1),
            cy: only.y.toFixed(1),
            r: 1.6,
          }),
        );
        return;
      }
      const confidence =
        segment.reduce((total, point) => total + point.confidence, 0) / segment.length;
      group.append(
        svgElement("polyline", {
          class: "observed-trace",
          points: segment.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" "),
          "stroke-opacity": (0.35 + 0.65 * confidence).toFixed(2),
        }),
      );
    });

    // A reading taken while the joint was hidden is marked, not smoothed away.
    plotted
      .filter((point) => point.visibility === "occluded")
      .forEach((point) => {
        group.append(
          svgElement("circle", {
            class: "observed-occluded",
            cx: point.x.toFixed(1),
            cy: point.y.toFixed(1),
            r: 2,
          }),
        );
      });

    const dot = svgElement("circle", { class: "observed-dot", r: 2.6, cx: left, cy: midY });
    const value = svgElement("text", {
      class: "observed-value",
      x: OBSERVED_VIEW.valueRight,
      y: midY + 3,
      "text-anchor": "end",
    });
    group.append(dot, value);
    observedCanvas.append(group);
    return { track, points: plotted, midY, dot, value };
  });

  const axisY = height - OBSERVED_VIEW.bottomPad + 14;
  [
    [left, "start", preview.span_start_seconds],
    [right, "end", preview.span_end_seconds],
  ].forEach(([x, anchor, seconds]) => {
    const stamp = svgElement("text", {
      class: "observed-axis",
      x,
      y: axisY,
      "text-anchor": anchor,
    });
    stamp.textContent = `${seconds.toFixed(1)} s`;
    observedCanvas.append(stamp);
  });

  const playhead = svgElement("line", {
    class: "observed-playhead",
    x1: left,
    y1: OBSERVED_VIEW.topPad - 4,
    x2: left,
    y2: height - OBSERVED_VIEW.bottomPad + 4,
  });
  observedCanvas.append(playhead);

  observedScene = { preview, rows, playhead, title, description, at, scale };
  drawObservedFrame(observedTime);
}

/* Read one joint at one instant, without inventing what happened between two
   strokes. Inside a stroke the angle is interpolated; across a break, and
   outside the joint's own span, the answer is that there is no reading. */
function observedReadingAt(points, seconds) {
  if (!points.length) return null;
  if (seconds < points[0].timestamp_seconds) return null;
  for (let index = 0; index < points.length - 1; index += 1) {
    const from = points[index];
    const to = points[index + 1];
    if (seconds < from.timestamp_seconds || seconds > to.timestamp_seconds) continue;
    if (to.starts_segment) return null;
    const width = to.timestamp_seconds - from.timestamp_seconds;
    const ratio = width > 0 ? (seconds - from.timestamp_seconds) / width : 0;
    return {
      angle: from.angle_degrees + (to.angle_degrees - from.angle_degrees) * ratio,
      x: from.x + (to.x - from.x) * ratio,
      y: from.y + (to.y - from.y) * ratio,
    };
  }
  const last = points[points.length - 1];
  if (seconds > last.timestamp_seconds) return null;
  return { angle: last.angle_degrees, x: last.x, y: last.y };
}

function drawObservedFrame(offsetSeconds) {
  if (!observedScene) return;
  const preview = observedScene.preview;
  const span = preview.duration_seconds;
  const clamped = span > 0 ? Math.min(Math.max(0, offsetSeconds), span) : 0;
  const seconds = preview.span_start_seconds + clamped;
  const x = observedScene.at(seconds);
  observedScene.playhead.setAttribute("x1", x.toFixed(1));
  observedScene.playhead.setAttribute("x2", x.toFixed(1));

  const gap = translations[currentLanguage].observedOccluded;
  observedScene.rows.forEach((row) => {
    const reading = observedReadingAt(row.points, seconds);
    if (reading) {
      row.dot.setAttribute("cx", reading.x.toFixed(1));
      row.dot.setAttribute("cy", reading.y.toFixed(1));
      row.dot.style.display = "";
      row.value.textContent = `${Math.round(reading.angle)}°`;
      row.value.classList.remove("is-missing");
    } else {
      row.dot.style.display = "none";
      row.value.textContent = gap;
      row.value.classList.add("is-missing");
    }
  });

  const clock = `${clamped.toFixed(1)} s`;
  setContent("#observed-clock", clock);
  if (observedScrubber && span > 0) {
    const position = String(Math.round((clamped / span) * 1000));
    if (observedScrubber.value !== position) observedScrubber.value = position;
    observedScrubber.setAttribute("aria-valuetext", clock);
  }
}

function renderObservedMotion() {
  if (!observedPanel) return;
  const t = translations[currentLanguage];
  const preview = observedPreview;
  observedPanel.hidden = !preview || !preview.tracks.length;
  // The audit decides whether these numbers are observations at all. Drawing
  // them under a plain "from the video" badge is how somebody reads a
  // rejected set of samples as a measurement of their own footage.
  const verdict = preview?.evidence_verdict || "usable";
  const rejected = verdict === "not_evidence";
  const doubted = rejected || verdict === "suspect";
  observedPanel.dataset.verdict = verdict;
  setContent(
    "#observed-tag",
    rejected ? t.observedTagRejected : doubted ? t.observedTagSuspect : t.observedTag,
  );
  setContent("#observed-legend", t.observedLegend);
  observedPlayButton?.setAttribute("aria-label", observedIntent ? t.observedPause : t.observedPlay);
  observedPlayButton?.setAttribute("aria-pressed", String(observedIntent));
  const glyph = observedPlayButton?.querySelector("span");
  if (glyph) glyph.textContent = observedIntent ? "❚❚" : "▶";
  observedScrubber?.setAttribute("aria-label", t.observedScrubberLabel);
  if (observedPanel.hidden) return;

  const verdictNote = document.querySelector("#observed-verdict");
  if (verdictNote) {
    verdictNote.hidden = !doubted;
    verdictNote.textContent = rejected
      ? t.observedVerdictNotEvidence
      : doubted
        ? t.observedVerdictSuspect
        : "";
  }

  const points = preview.tracks.reduce((total, track) => total + track.point_count, 0);
  let summary = (doubted ? t.observedSummaryUnverified : t.observedSummary)
    .replace("{joints}", String(preview.tracks.length))
    .replace("{duration}", preview.duration_seconds.toFixed(1))
    .replace("{points}", String(points));
  if (preview.omitted_joint_count) {
    summary += t.observedOmitted.replace("{count}", String(preview.omitted_joint_count));
  }
  setContent("#observed-summary", summary);

  if (!observedScene) return;
  observedScene.title.textContent = t.observedTitle;
  observedScene.description.textContent = t.observedDescription
    .replace("{joints}", String(preview.tracks.length))
    .replace("{duration}", preview.duration_seconds.toFixed(1));
  drawObservedFrame(observedTime);
}

function observedFrameLoop(timestamp) {
  if (!observedPlaying || !observedPreview) return;
  const delta = observedLastTimestamp
    ? Math.min(0.25, (timestamp - observedLastTimestamp) / 1000)
    : 0;
  observedLastTimestamp = timestamp;
  observedTime += delta;
  if (observedTime >= observedPreview.duration_seconds) observedTime = 0;
  drawObservedFrame(observedTime);
  observedFrameId = requestAnimationFrame(observedFrameLoop);
}

function syncObservedPlayback() {
  const visible =
    Boolean(observedScene) &&
    document.body.classList.contains("workspace-open") &&
    workspace.dataset.workspaceView === "simulation";
  const shouldRun = observedIntent && visible;
  if (shouldRun === observedPlaying) return;
  observedPlaying = shouldRun;
  cancelAnimationFrame(observedFrameId);
  observedLastTimestamp = 0;
  if (observedPlaying) observedFrameId = requestAnimationFrame(observedFrameLoop);
}

function setObservedPlaying(playing) {
  observedIntent = playing && Boolean(observedScene);
  syncObservedPlayback();
  renderObservedMotion();
}

/* --- Teach: one screen, one button, one approval, one result ------------
   Every stage here already exists as its own control in the detailed views.
   This runs them in order and shows them as stages, so the person expresses
   intent once and still sees the machinery working -- the system is not
   reduced to video -> prompt. */

function teachCallCount() {
  return teachDestinationValue === "robot" ? 2 : 1;
}

function renderTeachConsent() {
  if (!teachConsentText) return;
  const t = translations[currentLanguage];
  const spend = lastSpendState;
  if (spend?.enforced) {
    teachConsentText.textContent = t.teachConsent
      .replace("{calls}", String(teachCallCount()))
      .replace("{remaining}", `${spendFigure(Number(spend.remaining ?? 0), Number(spend.ceiling ?? 0), Number(spend.spent ?? 0))} ${spend.currency}`);
  } else {
    teachConsentText.textContent = t.teachConsentNoCeiling.replace("{calls}", String(teachCallCount()));
  }
}

function renderTeachLabels() {
  if (!teachForm) return;
  const t = translations[currentLanguage];
  setContent("#teach-eyebrow", t.teachEyebrow);
  setContent("#teach-title", t.teachTitle);
  setContent("#teach-task-label", t.teachTaskLabel);
  teachTask.placeholder = t.teachTaskPlaceholder;
  setContent("#teach-url-label", t.teachUrlLabel);
  teachUrl.placeholder = t.teachUrlPlaceholder;
  setContent("#teach-destination-label", t.teachDestinationLabel);
  setContent("#teach-robot-label", t.teachRobot);
  setContent("#teach-robot-help", t.teachRobotHelp);
  setContent("#teach-computer-label", t.teachComputer);
  setContent("#teach-computer-help", t.teachComputerHelp);
  teachTargetLabel.textContent = teachDestinationValue === "robot" ? t.teachTargetRobot : t.teachTargetComputer;
  teachTarget.placeholder = teachDestinationValue === "robot" ? t.teachTargetPlaceholderRobot : t.teachTargetPlaceholderComputer;
  setContent("#teach-advanced", t.teachAdvanced);
  setContent("#teach-start", `${t.teachStart} <span aria-hidden="true">→</span>`, true);
  setContent("#teach-progress-label", t.teachProgressLabel);
  setContent("#teach-retry", t.teachRetry);
  setContent("#teach-approval-label", t.teachApprovalLabel);
  setContent("#teach-reject", t.teachReject);
  setContent("#teach-approve", t.teachApprove);
  setContent("#teach-result-eyebrow", t.teachResultEyebrow);
  setContent("#teach-view-detail", t.teachViewDetail);
  setContent("#teach-view-simulation", t.teachViewSimulation);
  setContent("#teach-download", `${t.teachDownload} <span aria-hidden="true">↓</span>`, true);
  setContent("#teach-download-note", t.teachDownloadNote);
  renderTeachConsent();
  if (teachStages.length) renderTeachStages();
}

function renderTeachStages() {
  const t = translations[currentLanguage];
  teachStagesList.replaceChildren();
  const elapsed = teachStageStartedAt ? Math.round((Date.now() - teachStageStartedAt) / 1000) : 0;
  teachStages.forEach((key, index) => {
    const state = teachStatus[key] || "pending";
    const item = document.createElement("li");
    item.dataset.state = state;
    const number = document.createElement("span");
    number.textContent = String(index + 1).padStart(2, "0");
    const body = document.createElement("div");
    const title = document.createElement("b");
    title.textContent = t.teachStages[key][0];
    const detail = document.createElement("small");
    detail.textContent = t.teachStages[key][1];
    body.append(title, detail);
    const label = document.createElement("span");
    label.className = "teach-stage-state";
    // A running stage shows how long it has been running: nobody should have
    // to wonder whether the page is alive.
    label.textContent = state === "running" ? `${t.teachStates[state]} · ${elapsed} s` : t.teachStates[state];
    item.append(number, body, label);
    teachStagesList.append(item);
  });
}

function setTeachStage(key, state) {
  teachStatus[key] = state;
  if (state === "running") {
    teachStageStartedAt = Date.now();
    clearInterval(teachTicker);
    teachTicker = window.setInterval(renderTeachStages, 1000);
  } else if (!Object.values(teachStatus).includes("running")) {
    clearInterval(teachTicker);
    teachTicker = null;
    teachStageStartedAt = 0;
  }
  renderTeachStages();
}

function failTeach(detail) {
  Object.keys(teachStatus).forEach((key) => {
    if (teachStatus[key] === "running" || teachStatus[key] === "waiting") teachStatus[key] = "failed";
  });
  clearInterval(teachTicker);
  teachTicker = null;
  teachStageStartedAt = 0;
  renderTeachStages();
  teachProgressError.textContent = detail;
  teachProgress.hidden = false;
  teachApproval.hidden = true;
  teachRetry.hidden = false;
  teachRunning = false;
  setButtonBusy(teachStart, false);
  teachStart.disabled = false;
}

function resetTeachToForm() {
  teachProgress.hidden = true;
  teachApproval.hidden = true;
  teachResult.hidden = true;
  teachProgressError.textContent = "";
  teachRetry.hidden = true;
  teachForm.hidden = false;
  teachConsent.checked = false;
  teachStages = [];
  teachStatus = {};
  renderTeachConsent();
  teachTask.focus({ preventScroll: true });
}

function teachSelectedDestination() {
  return teachDestinationInputs.find((input) => input.checked)?.value || "robot";
}

async function startTeaching() {
  const t = translations[currentLanguage];
  teachError.textContent = "";
  const task = teachTask.value.trim();
  const url = teachUrl.value.trim();
  const destination = teachSelectedDestination();
  teachDestinationValue = destination;
  if (task.length < 12) { teachError.textContent = t.teachTaskError; teachTask.focus(); return; }
  if (!/^https?:\/\//i.test(url)) { teachError.textContent = t.teachUrlError; teachUrl.focus(); return; }
  if (teachTarget.value.trim().length < 2) { teachError.textContent = t.teachTargetError; teachTarget.focus(); return; }
  if (!teachConsent.checked) { teachError.textContent = t.teachConsentError; return; }
  if (missingSpendToken()) { teachError.textContent = t.spendTokenMissing; spendTokenInput.focus({ preventScroll: true }); return; }
  if (teachRunning) return;

  teachRunning = true;
  setButtonBusy(teachStart, true);
  teachStart.disabled = true;
  teachStages = destination === "robot"
    ? ["project", "extract", "review", "adapt", "motion", "ready"]
    : ["project", "extract", "review", "adapt", "ready"];
  teachStatus = Object.fromEntries(teachStages.map((key) => [key, "pending"]));
  teachForm.hidden = true;
  teachProgress.hidden = false;
  teachProgressError.textContent = "";
  teachRetry.hidden = true;
  teachApproval.hidden = true;
  teachResult.hidden = true;
  renderTeachStages();

  try {
    setTeachStage("project", "running");
    const payload = { task_description: task, destination, language: currentLanguage };
    const target = teachTarget.value.trim();
    if (destination === "robot") payload.robot_model = target;
    else payload.computer_application = target;
    const response = await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const project = await response.json();
    if (!response.ok) throw new Error(failureDetail(response, project));
    if (!project.is_sufficiently_clear) {
      throw new Error(project.clarification_questions?.[0]?.question || t.projectError);
    }
    // Keep the detailed views coherent with what was just done here.
    taskInput.value = task;
    videoUrl.value = url;
    const wizardRadio = document.querySelector(`input[name="destination"][value="${destination}"]`);
    if (wizardRadio && !wizardRadio.checked) {
      wizardRadio.checked = true;
      wizardRadio.dispatchEvent(new Event("change", { bubbles: true }));
    }
    configureVideoProcedure(project, url);
    loadRecentWork();
    setTeachStage("project", "done");

    setTeachStage("extract", "running");
    videoCostApproval.checked = true;
    await extractProjectVideoProcedure();
    if (videoProcedureRecord?.status !== "awaiting_review") {
      throw new Error(
        videoProcedureError.textContent
        || videoProcedureRecord?.failure_message
        || t.videoExtractionError,
      );
    }
    setTeachStage("extract", "done");

    setTeachStage("review", "waiting");
    renderTeachApproval();
  } catch (error) {
    console.error(error);
    failTeach(thrownDetail(error));
  } finally {
    refreshSpendState();
  }
}

function renderTeachApproval() {
  const procedure = videoProcedureRecord?.procedure;
  if (!procedure) return;
  setContent("#teach-approval-task", procedure.task);
  setContent("#teach-approval-objective", procedure.objective);
  const list = document.querySelector("#teach-steps");
  list.replaceChildren();
  procedure.steps.forEach((step) => {
    const item = document.createElement("li");
    const stamps = (step.source_timestamps || []).join(" · ");
    if (stamps) {
      const time = document.createElement("time");
      time.textContent = stamps;
      item.append(time);
    }
    const action = document.createElement("b");
    action.textContent = step.action;
    item.append(action);
    if (step.evidence) {
      const evidence = document.createElement("span");
      evidence.textContent = step.evidence;
      item.append(evidence);
    }
    list.append(item);
  });
  teachApproval.hidden = false;
  teachApprove.disabled = false;
  teachReject.disabled = false;
  requestAnimationFrame(() => teachApprove.focus({ preventScroll: true }));
}

async function decideTeaching(decision) {
  const t = translations[currentLanguage];
  const button = decision === "approve" ? teachApprove : teachReject;
  teachApprove.disabled = true;
  teachReject.disabled = true;
  setButtonBusy(button, true);
  try {
    await reviewProjectVideoProcedure(decision);
    if (decision === "reject") {
      setTeachStage("review", "failed");
      failTeach(t.teachRejected);
      return;
    }
    if (videoProcedureRecord?.status !== "approved") {
      throw new Error(videoProcedureError.textContent || t.teachReviewError);
    }
    setTeachStage("review", "done");
    teachApproval.hidden = true;

    setTeachStage("adapt", "running");
    await loadAdaptationPlan();
    setTeachStage("adapt", adaptationPlan ? "done" : "failed");

    if (teachStages.includes("motion")) {
      setTeachStage("motion", "running");
      motionCostApproval.checked = true;
      await runMotionAnalysis();
      setTeachStage("motion", motionAnalysis ? "done" : "failed");
      if (motionAnalysis) await loadAdaptationPlan();
    }

    setTeachStage("ready", "done");
    teachRunning = false;
    setButtonBusy(teachStart, false);
    teachStart.disabled = false;
    renderTeachResult();
  } catch (error) {
    console.error(error);
    failTeach(thrownDetail(error));
  } finally {
    setButtonBusy(button, false);
    refreshSpendState();
  }
}

function renderTeachResult() {
  const t = translations[currentLanguage];
  const procedure = videoProcedureRecord?.procedure;
  teachProgress.hidden = true;
  teachResult.hidden = false;
  teachResultError.textContent = "";
  setContent("#teach-result-title", procedure?.task || "");
  setContent("#teach-result-summary", adaptationPlan ? adaptationSummaryText() : t.teachNoPlan);
  const missing = document.querySelector("#teach-result-missing");
  missing.replaceChildren();
  (adaptationPlan?.missing_evidence || []).forEach((text) => {
    const item = document.createElement("li");
    item.textContent = text;
    missing.append(item);
  });
  let motionText = "";
  if (motionAnalysis) {
    motionText = t.simulationMotionSummary
      .replace("{subject}", motionAnalysis.subject_kind)
      .replace("{chain}", motionAnalysis.kinematic_chain)
      .replace("{samples}", String(motionAnalysis.sample_count))
      .replace("{joints}", String(motionAnalysis.distinct_joint_count))
      .replace("{span}", motionAnalysis.observed_span_seconds.toFixed(1))
      .replace("{confidence}", motionAnalysis.mean_confidence.toFixed(2));
  } else if (teachStages.includes("motion") && motionError.textContent) {
    motionText = t.teachMotionFailed.replace("{detail}", motionError.textContent);
  }
  setContent("#teach-result-motion", motionText);
  teachViewSimulation.hidden = teachDestinationValue !== "robot";
  setContent("#teach-download-note", t.teachDownloadNote);
  requestAnimationFrame(() => teachDownload.focus({ preventScroll: true }));
}

async function downloadAgent() {
  const t = translations[currentLanguage];
  if (!currentProject) return;
  teachResultError.textContent = "";
  setButtonBusy(teachDownload, true);
  teachDownload.disabled = true;
  setContent("#teach-download-note", t.teachDownloading);
  try {
    const base = `/api/projects/${encodeURIComponent(currentProject.project_id)}/agent-packages`;
    const built = await fetch(base, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: currentLanguage }),
    });
    const manifest = await built.json();
    if (!built.ok) throw new Error(failureDetail(built, manifest));
    const file = await fetch(`${base}/${encodeURIComponent(manifest.package_id)}/download`);
    if (!file.ok) throw new Error(failureDetail(file, await file.json().catch(() => null)));
    const blob = await file.blob();
    const name = `${manifest.directory_name}.zip`;
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = name;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(href), 10000);
    setContent(
      "#teach-download-note",
      t.teachDownloaded.replace("{name}", name).replace("{files}", String(manifest.files.length)),
    );
  } catch (error) {
    console.error(error);
    teachResultError.textContent = thrownDetail(error);
    setContent("#teach-download-note", t.teachDownloadNote);
  } finally {
    setButtonBusy(teachDownload, false);
    teachDownload.disabled = false;
  }
}

function startSimulationFromReview() {
  mountSimulationConsole();
  renderSimulationEvidence();
  const simulationButton = workspaceViewButtons.find(
    (button) => button.dataset.workspaceTarget === "simulation",
  );
  if (simulationButton) simulationButton.hidden = false;
  setWorkspaceView("simulation");
  startProcessing(taskInput.value.trim(), "local-simulation://guided-demo", true);
}

function restartVideoExtraction() {
  videoProcedureRecord = null;
  videoCostApproval.checked = false;
  videoProcedureError.textContent = "";
  videoProcedureEvidence.hidden = true;
  renderVideoProcedureState();
  videoCostApproval.focus({ preventScroll: true });
}

/* Retained work: durable records are only useful if they can be reopened. */
function storedStatusLabel(status) {
  const t = translations[currentLanguage];
  const labels = {
    approved: t.recentWorkApproved,
    rejected: t.recentWorkRejected,
    awaiting_review: t.recentWorkAwaiting,
    extraction_failed: t.recentWorkFailed,
  };
  return labels[status] || t.recentWorkNoExtraction;
}

function renderRecentWork() {
  const t = translations[currentLanguage];
  setContent("#recent-work-label", t.recentWorkLabel);
  setContent("#recent-work-note", t.recentWorkNote);
  recentWork.hidden = storedProjects.length === 0;
  recentWorkList.textContent = "";
  storedProjects.forEach((entry) => {
    const task = entry.project.task_definition?.name
      || entry.project.task_definition?.objective
      || entry.project.project_id;
    const destination = entry.project.destination_contract?.destination === "computer"
      ? t.recentWorkComputer
      : t.recentWorkRobot;
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", t.recentWorkOpen.replace("{task}", task));
    const title = document.createElement("b");
    title.textContent = task;
    const meta = document.createElement("small");
    const left = document.createElement("span");
    left.textContent = destination;
    const right = document.createElement("span");
    right.textContent = storedStatusLabel(entry.latest?.status);
    meta.append(left, right);
    button.append(title, meta);
    button.addEventListener("click", () => openStoredProject(entry));
    item.append(button);
    recentWorkList.append(item);
  });
}

async function loadRecentWork() {
  try {
    const response = await fetch("/api/projects");
    if (!response.ok) throw new Error(`Project list failed: ${response.status}`);
    const projects = await response.json();
    const entries = await Promise.all(projects.map(async (project) => {
      const records = await fetch(
        `/api/projects/${encodeURIComponent(project.project_id)}/video-procedures`,
      ).then((result) => (result.ok ? result.json() : []));
      return { project, records, latest: records[records.length - 1] || null };
    }));
    storedProjects = entries.reverse();
    renderRecentWork();
  } catch (error) {
    storedProjects = [];
    recentWork.hidden = true;
    console.error(error);
  }
}

function openStoredProject(entry) {
  const project = entry.project;
  const contract = project.destination_contract || {};
  const destination = contract.destination === "computer" ? "computer" : "robot";
  taskInput.value = project.task_definition?.objective || "";
  const radio = document.querySelector(
    `input[name="destination"][value="${destination}"]`,
  );
  if (radio && !radio.checked) {
    radio.checked = true;
    radio.dispatchEvent(new Event("change", { bubbles: true }));
  }
  if (destination === "robot") robotModel.value = contract.robot_model || "";
  else computerApplication.value = contract.application || "";

  const latest = entry.latest;
  videoUrl.value = latest?.source_url || "";
  configureVideoProcedure(project, latest?.source_url || null);
  videoProcedureRecord = latest;
  const practiceViewButton = workspaceViewButtons.find(
    (button) => button.dataset.workspaceTarget === "practice",
  );
  practiceViewButton.hidden = destination !== "computer";
  computerPracticePanel.hidden = destination !== "computer";
  if (latest) {
    videoProcedureEvidence.hidden = false;
    videoCostApproval.checked = false;
  }
  renderVideoProcedureState();
  loadAdaptationPlan();
  loadMotionAnalysis();
  loadUploads();
  loadProcedureHistory();
  fillReview();
  showStep(4);
  showProjectFeedback(
    translations[currentLanguage].recentWorkOpened.replace("{id}", project.project_id),
  );
  setWorkspaceView(latest ? "video" : "setup");
}

async function loadAdaptationPlan() {
  adaptationPlan = null;
  if (!currentProject || videoProcedureRecord?.status !== "approved") return;
  try {
    const response = await fetch(
      `/api/projects/${encodeURIComponent(currentProject.project_id)}`
      + `/video-procedures/${encodeURIComponent(videoProcedureRecord.extraction_id)}`
      + `/adapt?language=${encodeURIComponent(currentLanguage)}`,
      { method: "POST" },
    );
    if (!response.ok) return;
    adaptationPlan = await response.json();
    renderVideoNextStep();
  } catch (error) {
    console.error(error);
  }
}

function adaptationSummaryText() {
  const t = translations[currentLanguage];
  if (!adaptationPlan) return "";
  const lines = [
    t.adaptationSummary
      .replace("{actionable}", String(adaptationPlan.actionable_step_count))
      .replace("{total}", String(adaptationPlan.steps.length)),
  ];
  if (adaptationPlan.missing_evidence.length) {
    lines.push(
      t.adaptationMissing.replace("{missing}", adaptationPlan.missing_evidence[0]),
    );
  }
  lines.push(t.adaptationBlocked);
  return lines.join(" ");
}

function renderVideoNextStep() {
  const t = translations[currentLanguage];
  const status = videoProcedureRecord?.status;
  setContent("#video-next-step-label", t.nextStepLabel);
  if (videoExtractionRunning || !status) {
    videoNextStep.hidden = true;
    videoNextStepHandler = null;
    return;
  }
  const isComputer = selectedDestination() === "computer";
  const plans = {
    awaiting_review: [t.nextStepAwaitingReview, "", null],
    approved: isComputer
      ? [t.nextStepApprovedComputer, t.nextStepPractice, () => setWorkspaceView("practice")]
      : [t.nextStepApprovedRobot, t.nextStepSimulate, startSimulationFromReview],
    rejected: [t.nextStepRejected, t.nextStepRetry, restartVideoExtraction],
    extraction_failed: [t.nextStepFailed, t.nextStepRetry, restartVideoExtraction],
  };
  const [message, actionLabel, handler] = plans[status] || ["", "", null];
  const summary = status === "approved" ? adaptationSummaryText() : "";
  renderMotionEvidence();
  renderEvidenceHistory();
  videoNextStep.hidden = !message;
  setContent("#video-next-step-text", summary ? `${summary} ${message}` : message);
  videoNextStepAction.hidden = !actionLabel;
  videoNextStepAction.textContent = actionLabel;
  videoNextStepHandler = handler;
}

function motionAnalysisUrl() {
  return `/api/projects/${encodeURIComponent(currentProject.project_id)}`
    + `/video-procedures/${encodeURIComponent(videoProcedureRecord.extraction_id)}`
    + "/motion-analysis";
}

async function loadMotionAnalysis() {
  motionAnalysis = null;
  observedPreview = null;
  observedPreviewKey = null;
  observedScene = null;
  if (!currentProject || videoProcedureRecord?.status !== "approved") {
    renderMotionEvidence();
    return;
  }
  try {
    const response = await fetch(motionAnalysisUrl());
    if (response.ok) motionAnalysis = await response.json();
  } catch (error) {
    console.error(error);
  }
  renderMotionEvidence();
}

async function runMotionAnalysis() {
  if (motionAnalysisRunning || !motionCostApproval.checked) return;
  if (missingSpendToken()) {
    motionError.textContent = translations[currentLanguage].spendTokenMissing;
    spendTokenInput.focus({ preventScroll: true });
    return;
  }
  motionError.textContent = "";
  motionAnalysisRunning = true;
  renderMotionEvidence();
  try {
    const response = await fetch(motionAnalysisUrl(), {
      method: "POST",
      headers: spendHeaders(),
      body: JSON.stringify({
        frames_per_second: MOTION_FPS,
        window_seconds: MOTION_WINDOW_SECONDS,
        window_start_seconds: 0,
        output_language: currentLanguage,
        acknowledge_cloud_cost: true,
      }),
    });
    const body = await response.json();
    if (response.ok) {
      motionAnalysis = body;
      observedPreview = null;
      observedPreviewKey = null;
      observedScene = null;
      motionCostApproval.checked = false;
      loadAdaptationPlan();
    } else {
      const t = translations[currentLanguage];
      const template = response.status === 422 ? t.motionBudget : t.motionFailed;
      motionError.textContent = template.replace(
        "{detail}",
        failureDetail(response, body),
      );
    }
  } catch (error) {
    console.error(error);
    motionError.textContent = translations[currentLanguage]
      .motionFailed.replace("{detail}", thrownDetail(error));
  } finally {
    motionAnalysisRunning = false;
    refreshSpendState();
    renderMotionEvidence();
  }
}

function motionVerdictLabel(verdict) {
  const t = translations[currentLanguage];
  if (verdict === "usable") return t.motionVerdictUsable;
  if (verdict === "suspect") return t.motionVerdictSuspect;
  return t.motionVerdictNotEvidence;
}

function motionFindingText(finding) {
  const template = translations[currentLanguage].motionFinding?.[finding.code];
  if (!template) return finding.message;
  return Object.entries(finding.values || {}).reduce(
    (text, [key, value]) => text.split(`{${key}}`).join(value),
    template,
  );
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes / 1024;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[unit]}`;
}

async function loadUploads() {
  storedUploads = [];
  if (currentProject) {
    try {
      const response = await fetch(
        `/api/projects/${encodeURIComponent(currentProject.project_id)}/uploads`,
      );
      if (response.ok) storedUploads = (await response.json()).uploads || [];
    } catch (error) {
      console.error(error);
    }
  }
  renderUploads();
}

async function storeSelectedVideo() {
  const t = translations[currentLanguage];
  const file = videoFile.files[0];
  if (!file || uploadRunning) return;
  if (!currentProject) {
    uploadError.textContent = t.uploadNeedsProject;
    return;
  }
  uploadRunning = true;
  uploadError.textContent = "";
  renderUploads();
  try {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch(
      `/api/projects/${encodeURIComponent(currentProject.project_id)}/uploads`,
      { method: "POST", body },
    );
    const payload = await response.json();
    if (response.ok) {
      videoFile.value = "";
      setContent("#file-label", t.selectVideo);
      await loadUploads();
    } else {
      uploadError.textContent = t.uploadFailed.replace(
        "{detail}",
        failureDetail(response, payload),
      );
    }
  } catch (error) {
    console.error(error);
    uploadError.textContent = t.uploadFailed.replace("{detail}", thrownDetail(error));
  } finally {
    uploadRunning = false;
    renderUploads();
  }
}

async function removeUpload(uploadId) {
  if (!currentProject) return;
  try {
    await fetch(
      `/api/projects/${encodeURIComponent(currentProject.project_id)}`
      + `/uploads/${encodeURIComponent(uploadId)}`,
      { method: "DELETE" },
    );
  } catch (error) {
    console.error(error);
  }
  loadUploads();
}

function renderUploads() {
  if (!uploadList) return;
  const t = translations[currentLanguage];
  setContent("#upload-note", t.uploadNote);
  storeVideoFileButton.textContent = uploadRunning ? t.uploadStoring : t.uploadStore;
  storeVideoFileButton.disabled = uploadRunning || !videoFile.files.length;
  setButtonBusy(storeVideoFileButton, uploadRunning);

  uploadList.replaceChildren();
  for (const upload of storedUploads) {
    const item = document.createElement("li");
    const text = document.createElement("span");
    const name = document.createElement("b");
    name.textContent = upload.original_filename;
    const meta = document.createElement("small");
    meta.textContent = t.uploadMeta
      .replace("{size}", formatBytes(upload.size_bytes))
      .replace("{hash}", upload.sha256.slice(0, 12));
    text.append(name, meta);
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = t.uploadRemove;
    remove.addEventListener("click", () => removeUpload(upload.upload_id));
    item.append(text, remove);
    uploadList.append(item);
  }
}

async function loadProcedureHistory() {
  procedureHistory = null;
  projectReconciliation = null;
  if (!currentProject) {
    renderEvidenceHistory();
    return;
  }
  const base = `/api/projects/${encodeURIComponent(currentProject.project_id)}`
    + "/video-procedures/history";
  try {
    const [history, reconciliation] = await Promise.all([
      fetch(`${base}/versions`),
      fetch(`${base}/reconciliation`),
    ]);
    if (history.ok) procedureHistory = await history.json();
    if (reconciliation.ok) projectReconciliation = await reconciliation.json();
  } catch (error) {
    console.error(error);
  }
  renderEvidenceHistory();
}

function appendChange(list, text) {
  const item = document.createElement("li");
  item.textContent = text;
  list.append(item);
}

function renderDiffChanges(diff) {
  const t = translations[currentLanguage];
  historyChanges.replaceChildren();
  for (const step of diff.steps) {
    if (step.kind === "unchanged") continue;
    if (step.kind === "added") {
      appendChange(
        historyChanges,
        t.historyStepAdded
          .replace("{step}", String(step.step))
          .replace("{after}", step.after || ""),
      );
    } else if (step.kind === "removed") {
      appendChange(
        historyChanges,
        t.historyStepRemoved
          .replace("{step}", String(step.step))
          .replace("{before}", step.before || ""),
      );
    } else {
      const item = document.createElement("li");
      const label = document.createElement("span");
      label.textContent = `${t.historyStepChanged.replace("{step}", String(step.step))} `;
      const before = document.createElement("del");
      before.textContent = step.before || "";
      const after = document.createElement("ins");
      after.textContent = step.after || "";
      item.append(label, before, document.createTextNode(" \u2192 "), after);
      historyChanges.append(item);
    }
  }
  for (const list of diff.lists) {
    for (const value of list.added) {
      appendChange(
        historyChanges,
        t.historyListAdded.replace("{field}", list.field).replace("{value}", value),
      );
    }
    for (const value of list.removed) {
      appendChange(
        historyChanges,
        t.historyListRemoved.replace("{field}", list.field).replace("{value}", value),
      );
    }
  }
}

function renderEvidenceHistory() {
  if (!evidenceHistory) return;
  const t = translations[currentLanguage];
  const versions = procedureHistory?.versions || [];
  evidenceHistory.hidden = versions.length === 0;
  if (!versions.length) return;

  setContent("#history-label", t.historyLabel);
  setContent(
    "#history-totals",
    t.historyTotals
      .replace("{versions}", String(versions.length))
      .replace("{calls}", String(procedureHistory.total_cloud_calls))
      .replace("{tokens}", String(procedureHistory.total_tokens)),
  );

  historyVersions.replaceChildren();
  for (const version of versions) {
    const item = document.createElement("li");
    const tag = document.createElement("b");
    tag.textContent = version.procedure_version
      ? t.historyVersion.replace("{version}", String(version.procedure_version))
      : "\u2014";
    const task = document.createElement("span");
    task.textContent = version.task || version.source_url;
    const meta = document.createElement("small");
    meta.textContent = t.historyVersionMeta
      .replace("{steps}", String(version.step_count))
      .replace("{status}", version.status.replace(/_/g, " "));
    item.append(tag, task, meta);
    historyVersions.append(item);
  }

  const diff = procedureHistory.latest_diff;
  historyDiff.hidden = !diff;
  if (diff) {
    setContent(
      "#history-diff-label",
      t.historyDiffLabel
        .replace("{from}", String(diff.from_version ?? "?"))
        .replace("{to}", String(diff.to_version ?? "?")),
    );
    const source = diff.same_source ? t.historySameSource : t.historyCrossSource;
    const summary = diff.has_changes
      ? t.historyDiffSummary
        .replace("{changed}", String(diff.changed_step_count))
        .replace("{added}", String(diff.added_step_count))
        .replace("{removed}", String(diff.removed_step_count))
        .replace("{unchanged}", String(diff.unchanged_step_count))
      : t.historyNoChanges;
    setContent("#history-diff-summary", `${summary} ${source}`);
    renderDiffChanges(diff);
  }

  historyReconciliation.hidden = !projectReconciliation;
  if (projectReconciliation) {
    const result = projectReconciliation.result;
    setContent("#reconciliation-label", t.reconciliationLabel);
    const independence = document.querySelector("#reconciliation-independence");
    independence.dataset.cross = String(projectReconciliation.is_cross_source);
    independence.textContent = projectReconciliation.independence_note;
    setContent(
      "#reconciliation-summary",
      t.reconciliationSummary
        .replace("{sources}", String(result.source_count))
        .replace("{distinct}", String(projectReconciliation.distinct_source_count))
        .replace("{confidence}", result.confidence.toFixed(2))
        .replace("{conflicts}", String(result.conflicts.length)),
    );
    reconciliationConflicts.replaceChildren();
    for (const line of [...result.conflicts, ...result.uncertainties].slice(0, 8)) {
      appendChange(reconciliationConflicts, line);
    }
  }
}

function renderMotionEvidence() {
  if (!motionEvidence) return;
  const t = translations[currentLanguage];
  const eligible = videoProcedureRecord?.status === "approved"
    && selectedDestination() === "robot";
  motionEvidence.hidden = !eligible;
  if (!eligible) {
    motionError.textContent = "";
    return;
  }

  setContent("#motion-evidence-label", t.motionLabel);
  setContent(
    "#motion-evidence-intro",
    t.motionIntro
      .replace("{fps}", String(MOTION_FPS))
      .replace("{window}", String(MOTION_WINDOW_SECONDS)),
  );
  setContent("#motion-cost-approval-text", t.motionAck);
  runMotionAnalysisButton.textContent = motionAnalysisRunning
    ? t.motionRunning
    : t.motionRun;
  runMotionAnalysisButton.disabled = motionAnalysisRunning
    || !motionCostApproval.checked;
  setButtonBusy(runMotionAnalysisButton, motionAnalysisRunning);

  motionResult.hidden = !motionAnalysis;
  motionFindings.replaceChildren();
  if (!motionAnalysis) return;

  const verdict = motionAnalysis.audit.verdict;
  const verdictNode = document.querySelector("#motion-verdict");
  verdictNode.dataset.verdict = verdict;
  verdictNode.textContent = motionVerdictLabel(verdict);
  setContent(
    "#motion-stats",
    t.motionStats
      .replace("{samples}", String(motionAnalysis.sample_count))
      .replace("{joints}", String(motionAnalysis.distinct_joint_count))
      .replace("{span}", motionAnalysis.observed_span_seconds.toFixed(1))
      .replace("{rate}", motionAnalysis.samples_per_second.toFixed(1))
      .replace("{confidence}", motionAnalysis.mean_confidence.toFixed(2))
      .replace("{tokens}", String(motionAnalysis.usage?.total_tokens ?? 0))
      .replace("{elapsed}", motionAnalysis.elapsed_seconds.toFixed(1)),
  );
  setContent("#motion-estimate", t.motionEstimate);
  for (const finding of motionAnalysis.audit.findings) {
    const item = document.createElement("li");
    item.textContent = motionFindingText(finding);
    motionFindings.append(item);
  }
  setContent("#motion-retarget", motionAnalysis.retarget.reason);
}

function renderVideoProcedureState() {
  if (!videoProcedurePanel) return;
  const t = translations[currentLanguage];
  videoProcedurePanel.classList.toggle("has-procedure", Boolean(videoProcedureRecord?.procedure));
  setContent("#extract-video-procedure", videoExtractionRunning ? t.extractingVideo : t.extractVideo, !videoExtractionRunning);
  const retryableFailure = videoProcedureRecord?.status === "extraction_failed";
  extractVideoButton.disabled = videoExtractionRunning || Boolean(videoProcedureRecord && !retryableFailure);
  setButtonBusy(extractVideoButton, videoExtractionRunning);
  videoProcedureEvidence.hidden = !videoExtractionRunning && !videoProcedureRecord;
  extractionActivity.hidden = !videoExtractionRunning;
  setContent("#extraction-activity-note", t.extractionActivityNote);
  setContent("#video-extraction-status", localizedVideoStatus(videoProcedureRecord?.status));
  renderVideoNextStep();

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
  setButtonBusy(approveVideoProcedureButton, false);
  setButtonBusy(rejectVideoProcedureButton, false);
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
  motionError.textContent = "";
  videoProcedurePanel.hidden = !sourceUrl;
  const videoViewButton = workspaceViewButtons.find((button) => button.dataset.workspaceTarget === "video");
  videoViewButton.hidden = !sourceUrl;
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
  if (missingSpendToken()) {
    videoProcedureError.textContent = t.spendTokenMissing;
    spendTokenInput.focus({ preventScroll: true });
    return;
  }
  videoExtractionRunning = true;
  startExtractionTimer();
  renderVideoProcedureState();
  await nextPaint();
  try {
    const response = await fetch(`/api/projects/${encodeURIComponent(currentProject.project_id)}/video-procedures/extract`, {
      method: "POST",
      headers: spendHeaders(),
      body: JSON.stringify({
        video_url: currentVideoSource,
        task_hint: taskInput.value.trim(),
        output_language: currentLanguage,
        acknowledge_source_approved: true,
        acknowledge_cloud_cost: true,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(failureDetail(response, payload));
    videoProcedureRecord = payload;
  } catch (error) {
    videoProcedureError.textContent = error.message || t.videoExtractionError;
    console.error(error);
  } finally {
    videoExtractionRunning = false;
    stopExtractionTimer();
    refreshSpendState();
    if (videoProcedureRecord?.status === "extraction_failed") videoCostApproval.checked = false;
    renderVideoProcedureState();
  }
}

async function reviewProjectVideoProcedure(decision) {
  const t = translations[currentLanguage];
  if (!currentProject || !videoProcedureRecord) return;
  approveVideoProcedureButton.disabled = true;
  rejectVideoProcedureButton.disabled = true;
  const decisionButton = decision === "approve" ? approveVideoProcedureButton : rejectVideoProcedureButton;
  setButtonBusy(decisionButton, true);
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
    loadRecentWork();
    loadAdaptationPlan();
    setButtonBusy(decisionButton, false);
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
  setButtonBusy(runBrowserPracticeButton, true);
  renderPracticeState();
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
    setButtonBusy(runBrowserPracticeButton, false);
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
  setButtonBusy(processSubmit, true);
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
    if (!response.ok) {
      throw new Error(failureDetail(response, await response.json().catch(() => null)));
    }
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
    loadRecentWork();
    const practiceViewButton = workspaceViewButtons.find((button) => button.dataset.workspaceTarget === "practice");
    practiceViewButton.hidden = destination !== "computer";
    if (destination === "robot") {
      computerPracticePanel.hidden = true;
      if (extractionSource) {
        setWorkspaceView("video");
      } else {
        closeWorkspace();
        window.setTimeout(() => startProcessing(taskInput.value.trim(), source), reducedMotion.matches ? 0 : 550);
      }
    } else {
      computerPracticePanel.hidden = false;
      browserPracticeApproval.checked = false;
      practiceEvidence.hidden = true;
      practiceRunResult = null;
      practiceActiveStage = -1;
      practiceCompletedStages = 0;
      renderPracticePlan();
      renderPracticeState();
      setWorkspaceView(extractionSource ? "video" : "practice");
    }
  } catch (error) {
    showProjectFeedback(t.projectFailed.replace("{detail}", thrownDetail(error)), true);
    console.error(error);
  } finally {
    processSubmit.disabled = false;
    setButtonBusy(processSubmit, false);
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
  // Never the user's task: this panel draws a built-in six-joint arm, and
  // labelling it "how a cheetah runs" is how somebody concludes the arm is
  // repeating their video.
  setContent(
    "#monitor-task",
    motionPreview?.robot_model
      ? t.builtInTrajectory.replace("{robot}", motionPreview.robot_model)
      : t.builtInTrajectoryIdle,
  );
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
  setMotionPreview(session.motion_preview || null);
  renderProcessState();
}

async function pollProcessingSession(sessionId) {
  try {
    const response = await fetch(`/api/processing/robot-motion/${encodeURIComponent(sessionId)}`);
    if (!response.ok) {
      throw new Error(failureDetail(response, await response.json().catch(() => null)));
    }
    const session = await response.json();
    applyProcessingSession(session);
    if (session.status === "processing") {
      processPollTimer = window.setTimeout(() => pollProcessingSession(sessionId), reducedMotion.matches ? 750 : 500);
    }
  } catch (error) {
    processStatus = "failed";
    processErrorMessage = translations[currentLanguage]
      .processFailedDetail.replace("{detail}", thrownDetail(error));
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
  motionTime = 0;
  drawMotionFrame(motionTime);
  if (motionPreview && !reducedMotion.matches) setMotionPlaying(true);
  renderProcessState();
  const processingSection = document.querySelector("#procesamiento");
  if (consoleIsInWorkspace()) {
    // Nothing to scroll to: the console is inside the fixed workspace overlay.
  } else if (immediate) {
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
    processErrorMessage = translations[currentLanguage]
      .processFailedDetail.replace("{detail}", thrownDetail(error));
    renderProcessState();
    console.error(error);
  }
}


/* Motion preview: redraws validated joint angles as a schematic projection.
   It draws stored waypoints; it is not a physics or collision simulation. */
const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
const MOTION_VIEW = { width: 240, height: 232, baseX: 132, baseY: 196, scale: 230, samples: 150 };
const MOTION_CAMERA = { azimuth: (24 * Math.PI) / 180, tilt: (20 * Math.PI) / 180 };
const MOTION_IDLE_PREVIEW = {
  robot_model: "",
  duration_seconds: 0,
  joints: [
    { joint_index: 0, label: "base", role: "base_yaw", length_ratio: 0 },
    { joint_index: 1, label: "shoulder", role: "planar_link", length_ratio: 0.42 },
    { joint_index: 2, label: "elbow", role: "planar_link", length_ratio: 0.28 },
    { joint_index: 3, label: "wrist", role: "planar_link", length_ratio: 0.16 },
  ],
  waypoints: [
    { timestamp_seconds: 0, joint_positions_degrees: [0, -14, 26, 40], gripper_percent: 100, label: "" },
    { timestamp_seconds: 0, joint_positions_degrees: [0, -14, 26, 40], gripper_percent: 100, label: "" },
  ],
};

function svgElement(tag, attributes = {}) {
  const element = document.createElementNS(SVG_NAMESPACE, tag);
  Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, String(value)));
  return element;
}

function rotateFrameZ(frame, degrees) {
  const radians = (degrees * Math.PI) / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);
  const [x, y, z] = frame;
  return [x.map((value, axis) => value * cos + y[axis] * sin), x.map((value, axis) => -value * sin + y[axis] * cos), z];
}

function rotateFrameY(frame, degrees) {
  const radians = (degrees * Math.PI) / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);
  const [x, y, z] = frame;
  return [x.map((value, axis) => value * cos - z[axis] * sin), y, x.map((value, axis) => value * sin + z[axis] * cos)];
}

function projectMotionPoint(point) {
  const [x, y, z] = point;
  const horizontal = x * Math.cos(MOTION_CAMERA.azimuth) + y * Math.sin(MOTION_CAMERA.azimuth);
  const depth = -x * Math.sin(MOTION_CAMERA.azimuth) + y * Math.cos(MOTION_CAMERA.azimuth);
  return {
    x: MOTION_VIEW.baseX + horizontal,
    y: MOTION_VIEW.baseY - (z * Math.cos(MOTION_CAMERA.tilt) + depth * Math.sin(MOTION_CAMERA.tilt)),
  };
}

function motionPose(preview, angles) {
  let frame = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  let point = [0, 0, 0];
  const chain = [point];
  preview.joints.forEach((joint) => {
    const angle = Number(angles[joint.joint_index] ?? 0);
    if (joint.role === "planar_link") {
      frame = rotateFrameY(frame, angle);
      const length = joint.length_ratio * MOTION_VIEW.scale;
      point = point.map((value, axis) => value + frame[2][axis] * length);
      chain.push(point);
    } else {
      frame = rotateFrameZ(frame, angle);
    }
  });
  return { chain: chain.map(projectMotionPoint), frame };
}

function motionStateAt(preview, time) {
  const waypoints = preview.waypoints;
  if (!waypoints.length) return { angles: [], gripper: null, waypointIndex: -1, label: "", time: 0 };
  const clamped = Math.min(Math.max(time, 0), preview.duration_seconds);
  let index = 0;
  while (index < waypoints.length - 2 && waypoints[index + 1].timestamp_seconds <= clamped) index += 1;
  const from = waypoints[index];
  const to = waypoints[Math.min(index + 1, waypoints.length - 1)];
  const span = to.timestamp_seconds - from.timestamp_seconds;
  const ratio = span > 0 ? Math.min(1, Math.max(0, (clamped - from.timestamp_seconds) / span)) : 0;
  const angles = from.joint_positions_degrees.map((value, joint) => value + ((to.joint_positions_degrees[joint] ?? value) - value) * ratio);
  const startGripper = from.gripper_percent;
  const gripper = startGripper === null || startGripper === undefined
    ? null
    : startGripper + ((to.gripper_percent ?? startGripper) - startGripper) * ratio;
  const waypointIndex = ratio < 0.5 ? index : Math.min(waypoints.length - 1, index + 1);
  return { angles, gripper, waypointIndex, label: waypoints[waypointIndex].label || "", time: clamped };
}

function buildMotionSamples(preview) {
  if (!preview.waypoints.length || preview.duration_seconds <= 0) return [];
  const samples = [];
  for (let index = 0; index <= MOTION_VIEW.samples; index += 1) {
    const time = (preview.duration_seconds * index) / MOTION_VIEW.samples;
    const pose = motionPose(preview, motionStateAt(preview, time).angles);
    samples.push({ time, point: pose.chain[pose.chain.length - 1] });
  }
  return samples;
}

function pointsAttribute(points) {
  return points.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");
}

function buildMotionScene(preview) {
  motionCanvas.textContent = "";
  motionCanvas.setAttribute("viewBox", `0 0 ${MOTION_VIEW.width} ${MOTION_VIEW.height}`);
  const title = svgElement("title", { id: "motion-canvas-title" });
  const description = svgElement("desc", { id: "motion-canvas-desc" });
  motionCanvas.append(title, description);
  motionCanvas.append(
    svgElement("line", { class: "motion-floor", x1: 16, y1: MOTION_VIEW.baseY, x2: MOTION_VIEW.width - 16, y2: MOTION_VIEW.baseY }),
    svgElement("ellipse", { class: "motion-pedestal", cx: MOTION_VIEW.baseX, cy: MOTION_VIEW.baseY, rx: 30, ry: 9 }),
  );

  const samples = buildMotionSamples(preview);
  const trailFull = svgElement("polyline", { class: "motion-trail-full", points: pointsAttribute(samples.map((sample) => sample.point)) });
  const trailLive = svgElement("polyline", { class: "motion-trail-live", points: "" });
  motionCanvas.append(trailFull, trailLive);

  const waypointDots = preview.waypoints.map((waypoint) => {
    const pose = motionPose(preview, waypoint.joint_positions_degrees);
    const tool = pose.chain[pose.chain.length - 1];
    const dot = svgElement("circle", { class: "motion-waypoint-dot", cx: tool.x.toFixed(1), cy: tool.y.toFixed(1), r: 2.4 });
    motionCanvas.append(dot);
    return dot;
  });

  const arm = svgElement("g");
  const linkCount = preview.joints.filter((joint) => joint.role === "planar_link").length;
  const shadows = [];
  const links = [];
  const joints = [];
  for (let index = 0; index < linkCount; index += 1) {
    shadows.push(svgElement("line", { class: "motion-link-shadow" }));
    links.push(svgElement("line", { class: "motion-link" }));
  }
  shadows.forEach((shadow) => arm.append(shadow));
  links.forEach((link) => arm.append(link));
  for (let index = 0; index <= linkCount; index += 1) {
    const joint = svgElement("circle", { class: "motion-joint", r: index === 0 ? 5.5 : 4 });
    joints.push(joint);
    arm.append(joint);
  }
  const gripper = svgElement("path", { class: "motion-gripper", d: "" });
  arm.append(gripper);
  motionCanvas.append(arm);

  const dials = [];
  const addDial = (joint, cx, cy, radius) => {
    const group = svgElement("g");
    const dialTitle = svgElement("title");
    dialTitle.textContent = joint.label;
    const needle = svgElement("line", { class: "motion-dial-needle", x1: cx, y1: cy, x2: cx, y2: cy - radius * 0.82 });
    const value = svgElement("text", { class: "motion-dial-value", x: cx, y: cy + radius + 9 });
    const name = svgElement("text", { class: "motion-dial-label", x: cx, y: cy - radius - 4 });
    name.textContent = `J${joint.joint_index}`;
    group.append(dialTitle, svgElement("circle", { class: "motion-dial-ring", cx, cy, r: radius }), needle, value, name);
    motionCanvas.append(group);
    dials.push({ joint, cx, cy, radius, needle, value });
  };
  const yawJoint = preview.joints.find((joint) => joint.role === "base_yaw");
  if (yawJoint) addDial(yawJoint, 40, 150, 22);
  preview.joints.filter((joint) => joint.role === "roll").slice(0, 3).forEach((joint, index) => {
    addDial(joint, MOTION_VIEW.width - 24, 42 + index * 54, 15);
  });

  motionScene = { preview, samples, title, description, trailLive, waypointDots, shadows, links, joints, gripper, dials };
}

function drawMotionFrame(time) {
  if (!motionScene) return;
  const preview = motionScene.preview;
  const state = motionStateAt(preview, time);
  const pose = motionPose(preview, state.angles);

  motionScene.shadows.forEach((shadow, index) => {
    const from = pose.chain[index];
    const to = pose.chain[index + 1];
    [shadow, motionScene.links[index]].forEach((line) => {
      line.setAttribute("x1", from.x.toFixed(1));
      line.setAttribute("y1", from.y.toFixed(1));
      line.setAttribute("x2", to.x.toFixed(1));
      line.setAttribute("y2", to.y.toFixed(1));
    });
  });
  motionScene.joints.forEach((joint, index) => {
    const point = pose.chain[index];
    if (!point) return;
    joint.setAttribute("cx", point.x.toFixed(1));
    joint.setAttribute("cy", point.y.toFixed(1));
  });

  const tool = pose.chain[pose.chain.length - 1];
  const previous = pose.chain[pose.chain.length - 2] || { x: tool.x, y: tool.y - 1 };
  const axisLength = Math.hypot(tool.x - previous.x, tool.y - previous.y) || 1;
  const axis = { x: (tool.x - previous.x) / axisLength, y: (tool.y - previous.y) / axisLength };
  const fingerPlane = projectMotionPoint(pose.frame[0].map((value) => value * 12));
  const spreadX = fingerPlane.x - MOTION_VIEW.baseX;
  const spreadY = fingerPlane.y - MOTION_VIEW.baseY;
  const spreadLength = Math.hypot(spreadX, spreadY) || 1;
  const opening = 2 + ((state.gripper ?? 100) / 100) * 5;
  motionScene.gripper.setAttribute("d", [1, -1].map((side) => {
    const originX = tool.x + (spreadX / spreadLength) * opening * side;
    const originY = tool.y + (spreadY / spreadLength) * opening * side;
    return `M ${originX.toFixed(1)} ${originY.toFixed(1)} l ${(axis.x * 9).toFixed(1)} ${(axis.y * 9).toFixed(1)}`;
  }).join(" "));

  const livePoints = motionScene.samples.filter((sample) => sample.time <= state.time).map((sample) => sample.point);
  livePoints.push(tool);
  motionScene.trailLive.setAttribute("points", pointsAttribute(livePoints));
  motionScene.waypointDots.forEach((dot, index) => dot.classList.toggle("is-current", index === state.waypointIndex));

  motionScene.dials.forEach((dial) => {
    const angle = Number(state.angles[dial.joint.joint_index] ?? 0);
    const radians = (angle * Math.PI) / 180;
    dial.needle.setAttribute("x2", (dial.cx + Math.sin(radians) * dial.radius * 0.82).toFixed(1));
    dial.needle.setAttribute("y2", (dial.cy - Math.cos(radians) * dial.radius * 0.82).toFixed(1));
    dial.value.textContent = `${Math.round(angle)}°`;
  });

  renderMotionReadout(state);
}

function renderMotionReadout(state) {
  const t = translations[currentLanguage];
  const hasPreview = Boolean(motionPreview);
  const clock = `${state.time.toFixed(1)} s`;
  setContent("#motion-clock", hasPreview ? clock : "0.0 s");
  const phase = hasPreview
    ? `${t.motionPhase} ${state.waypointIndex + 1}/${motionPreview.waypoints.length}${state.label ? ` · ${state.label}` : ""}`
    : t.motionIdlePhase;
  setContent("#motion-phase", phase);
  const gripper = !hasPreview || state.gripper === null || state.gripper === undefined
    ? t.motionNoGripper
    : t.motionGripper.replace("{percent}", String(Math.round(state.gripper)));
  setContent("#motion-gripper", gripper);
  if (hasPreview && motionPreview.duration_seconds > 0) {
    const position = Math.round((state.time / motionPreview.duration_seconds) * 1000);
    if (String(position) !== motionScrubber.value) motionScrubber.value = String(position);
    if (motionScrubber.getAttribute("aria-valuetext") !== clock) motionScrubber.setAttribute("aria-valuetext", clock);
  }
  motionTicks.querySelectorAll("button").forEach((tick, index) => tick.classList.toggle("is-current", index === state.waypointIndex));
}

function renderMotionLabels() {
  const t = translations[currentLanguage];
  motionPlayButton.setAttribute("aria-label", motionIntent ? t.motionPause : t.motionPlay);
  motionPlayButton.querySelector("span").textContent = motionIntent ? "❚❚" : "▶";
  motionScrubber.setAttribute("aria-label", t.motionScrubberLabel);
  setContent("#motion-legend", t.motionLegend);
  if (!motionScene) return;
  motionScene.title.textContent = t.motionTitle;
  motionScene.description.textContent = motionPreview
    ? t.motionDescription
        .replace("{robot}", motionPreview.robot_model)
        .replace("{count}", String(motionPreview.waypoints.length))
        .replace("{duration}", motionPreview.duration_seconds.toFixed(1))
    : t.motionIdleDescription;
  motionTicks.querySelectorAll("button").forEach((tick, index) => {
    const waypoint = motionPreview?.waypoints[index];
    if (!waypoint) return;
    tick.setAttribute("aria-label", t.motionJump.replace("{label}", waypoint.label || `${index + 1}`).replace("{time}", waypoint.timestamp_seconds.toFixed(1)));
  });
}

function renderMotionTicks() {
  motionTicks.textContent = "";
  if (!motionPreview || motionPreview.duration_seconds <= 0) return;
  motionPreview.waypoints.forEach((waypoint, index) => {
    const tick = document.createElement("button");
    tick.type = "button";
    tick.style.left = `${(waypoint.timestamp_seconds / motionPreview.duration_seconds) * 100}%`;
    tick.addEventListener("click", () => {
      setMotionPlaying(false);
      motionTime = waypoint.timestamp_seconds;
      drawMotionFrame(motionTime);
    });
    motionTicks.append(tick);
  });
}

function motionFrameLoop(timestamp) {
  if (!motionPlaying || !motionPreview) return;
  const delta = motionLastTimestamp ? Math.min(0.25, (timestamp - motionLastTimestamp) / 1000) : 0;
  motionLastTimestamp = timestamp;
  motionTime += delta;
  if (motionTime >= motionPreview.duration_seconds) motionTime = 0;
  drawMotionFrame(motionTime);
  motionFrameId = requestAnimationFrame(motionFrameLoop);
}

function syncMotionPlayback() {
  const visible = motionOnScreen && !document.body.classList.contains("workspace-open");
  const shouldRun = motionIntent && Boolean(motionPreview) && visible;
  if (shouldRun === motionPlaying) return;
  motionPlaying = shouldRun;
  cancelAnimationFrame(motionFrameId);
  motionLastTimestamp = 0;
  if (motionPlaying) motionFrameId = requestAnimationFrame(motionFrameLoop);
}

function setMotionPlaying(playing) {
  const canPlay = Boolean(motionPreview) && motionPreview.duration_seconds > 0;
  motionIntent = playing && canPlay;
  motionPlayButton.setAttribute("aria-pressed", String(motionIntent));
  syncMotionPlayback();
  renderMotionLabels();
}

function setMotionPreview(preview) {
  const key = preview ? JSON.stringify(preview) : "";
  if (key === motionPreviewKey) return;
  motionPreviewKey = key;
  motionPreview = preview;
  motionTime = 0;
  buildMotionScene(preview || MOTION_IDLE_PREVIEW);
  document.querySelector("#motion-preview").classList.toggle("is-idle", !preview);
  motionPlayButton.disabled = !preview;
  motionScrubber.disabled = !preview;
  renderMotionTicks();
  renderMotionLabels();
  drawMotionFrame(0);
  setMotionPlaying(Boolean(preview) && !reducedMotion.matches);
}


function applyExample() {
  const t = translations[currentLanguage];
  const selectRadio = (name, value) => {
    const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
    if (!radio || radio.checked) return;
    radio.checked = true;
    radio.dispatchEvent(new Event("change", { bubbles: true }));
  };
  taskInput.value = t.exampleTask;
  selectRadio("destination", "robot");
  robotModel.value = t.exampleRobot;
  selectRadio("source-type", "youtube");
  videoUrl.value = t.exampleSource;
  taskError.textContent = "";
  destinationError.textContent = "";
  sourceError.textContent = "";
  fillReview();
  showStep(4);
  showProjectFeedback(t.exampleApplied);
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
    workspaceViewButtons.find((button) => button.dataset.workspaceTarget === "video").hidden = true;
    workspaceViewButtons.find((button) => button.dataset.workspaceTarget === "practice").hidden = true;
    setWorkspaceView("setup", false);
  });
});

document.querySelectorAll("input[name='source-type']").forEach((radio) => {
  radio.addEventListener("change", () => {
    document.querySelectorAll(".source-option").forEach((option) => option.classList.toggle("is-selected", option.contains(radio)));
    document.querySelectorAll("[data-source-panel]").forEach((panel) => { panel.hidden = panel.dataset.sourcePanel !== radio.value; });
    if (radio.value === "automatic" && !sourceQuery.value.trim()) sourceQuery.value = taskInput.value.trim();
    sourceError.textContent = "";
    renderUploads();
    // Choosing YouTube or automatic search redefines the source that will be
    // extracted, so an already created project no longer matches the form.
    // A local video is extra evidence kept beside the project, not a new
    // source, so it must not discard the project it is being added to.
    if (radio.value === "upload") return;
    currentProject = null;
    computerPracticePanel.hidden = true;
    videoProcedurePanel.hidden = true;
    workspaceViewButtons.find((button) => button.dataset.workspaceTarget === "video").hidden = true;
    workspaceViewButtons.find((button) => button.dataset.workspaceTarget === "practice").hidden = true;
    setWorkspaceView("setup", false);
  });
});

videoFile.addEventListener("change", () => {
  setContent(
    "#file-label",
    videoFile.files[0]?.name || translations[currentLanguage].selectVideo,
  );
  uploadError.textContent = "";
  renderUploads();
});
storeVideoFileButton.addEventListener("click", storeSelectedVideo);
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
procedureStepPrevious.addEventListener("click", () => { currentProcedureStep -= 1; renderProcedureStepPage(); });
procedureStepNext.addEventListener("click", () => { currentProcedureStep += 1; renderProcedureStepPage(); });
document.querySelectorAll('a[href="#entrenar"]').forEach((anchor) => anchor.addEventListener("click", (event) => {
  event.preventDefault();
  openWorkspace("teach", anchor);
}));
workspaceCloseButton.addEventListener("click", closeWorkspace);
spendTokenInput.addEventListener("input", rememberSpendToken);
teachStart.addEventListener("click", startTeaching);
teachAdvanced.addEventListener("click", () => setWorkspaceView("setup"));
teachRetry.addEventListener("click", resetTeachToForm);
teachApprove.addEventListener("click", () => decideTeaching("approve"));
teachReject.addEventListener("click", () => decideTeaching("reject"));
teachViewDetail.addEventListener("click", () => setWorkspaceView("video"));
teachViewSimulation.addEventListener("click", startSimulationFromReview);
teachDownload.addEventListener("click", downloadAgent);
teachDestinationInputs.forEach((input) => input.addEventListener("change", () => {
  teachDestinationValue = input.value;
  teachDestinationInputs.forEach((other) => other.closest(".teach-destination").classList.toggle("is-selected", other.checked));
  renderTeachLabels();
}));
workspaceViewButtons.forEach((button) => button.addEventListener("click", () => setWorkspaceView(button.dataset.workspaceTarget)));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && document.body.classList.contains("workspace-open")) closeWorkspace();
  trapWorkspaceFocus(event);
});
[browserTargetUrl, browserTextSelector, browserSampleText].forEach((input) => input.addEventListener("input", () => {
  browserPracticeApproval.checked = false;
  browserPracticeError.textContent = "";
  renderPracticePlan();
}));

motionPlayButton.addEventListener("click", () => setMotionPlaying(!motionIntent));
if (typeof IntersectionObserver === "function") {
  new IntersectionObserver((entries) => {
    motionOnScreen = entries.some((entry) => entry.isIntersecting);
    syncMotionPlayback();
  }, { threshold: 0.15 }).observe(document.querySelector(".source-monitor"));
}
motionScrubber.addEventListener("input", () => {
  if (!motionPreview) return;
  setMotionPlaying(false);
  motionTime = (Number(motionScrubber.value) / 1000) * motionPreview.duration_seconds;
  drawMotionFrame(motionTime);
});
observedPlayButton?.addEventListener("click", () => setObservedPlaying(!observedIntent));
observedScrubber?.addEventListener("input", () => {
  if (!observedPreview) return;
  // Read the dragged position first: pausing redraws the frame, and that
  // redraw writes the playing position back into this very input.
  const ratio = Number(observedScrubber.value) / 1000;
  setObservedPlaying(false);
  observedTime = ratio * observedPreview.duration_seconds;
  drawObservedFrame(observedTime);
});
useExampleButton.addEventListener("click", applyExample);
videoNextStepAction.addEventListener("click", () => videoNextStepHandler?.());
motionCostApproval.addEventListener("change", renderMotionEvidence);
runMotionAnalysisButton.addEventListener("click", runMotionAnalysis);
stepJumpButtons.forEach((button) => button.addEventListener("click", () => { if (!button.disabled) showStep(Number(button.dataset.stepJump)); }));
[robotModel, computerApplication, videoUrl].forEach((input) => input.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  event.preventDefault();
  if (!validateCurrentStep()) return;
  if (currentStep === 3) fillReview();
  showStep(Math.min(4, currentStep + 1));
}));
sourceQuery.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  event.preventDefault();
  searchAutomaticSources();
});
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
setMotionPreview(null);
applyLanguage(preferredLanguage);
loadRecentWork();
if (location.hash === "#entrenar") openWorkspace("teach", null);
fetch("/api/status")
  .then((response) => (response.ok ? response.json() : null))
  .then((status) => {
    renderSpendRemaining(status?.spend);
    spendTokenRequired = Boolean(status?.spend_token_required);
    if (!spendTokenRequired) return;
    spendTokenField.hidden = false;
    try { spendTokenInput.value = sessionStorage.getItem(SPEND_TOKEN_KEY) || ""; } catch (_) { /* Ask for it again. */ }
    spendTokenField.classList.toggle("is-set", Boolean(spendTokenInput.value));
  })
  .catch(() => { /* The field stays hidden; a paid call will say why. */ });
fetch("/health").then((response) => { if (!response.ok) throw new Error("Health check failed"); return response.json(); }).then(() => { systemChecked = true; systemOnline = true; updateSystemStatus(); }).catch(() => { systemChecked = true; systemOnline = false; updateSystemStatus(); });
