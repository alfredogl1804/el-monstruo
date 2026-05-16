/**
 * La Forja — pasos canónicos del tour onboarding.
 *
 * Sprint LA-FORJA-001 D3.1.
 *
 * 7 pasos estáticos. Sin LLM. Copywriting Brand DNA (forja industrial,
 * lenguaje directo, sin corporativismo, sin emojis decorativos).
 *
 * Estructura: cada paso es data, no markup. La UI los renderiza
 * vía `Tour.tsx` y `StepShell.tsx`. Esto permite que tests verifiquen
 * el contrato (count = 7, ids únicos, ningún placeholder vacío) sin
 * tocar JSX.
 */

export interface ForjaTourStep {
  id: string;
  /** Etiqueta corta arriba del título (ej: "Paso 2 de 7"). */
  eyebrow: string;
  /** Título principal del paso. Una sola oración fuerte. */
  title: string;
  /**
   * Cuerpo del paso. Array de párrafos. Cada string es un `<p>`.
   * No HTML. Si necesitas énfasis, viene de `highlights`.
   */
  body: readonly string[];
  /**
   * Frases que la UI puede destacar dentro del body (bold, accent
   * color). Cada string debe aparecer literal en algún `body[i]`.
   */
  highlights?: readonly string[];
  /**
   * Lista bullet opcional al pie del paso. Cada item con verbo
   * directo, sin floreo.
   */
  bullets?: readonly string[];
  /**
   * Texto del CTA principal del paso. Si es el último paso, esto
   * es el botón "Terminar". El botón "Anterior" siempre es genérico.
   */
  cta: string;
}

export const FORJA_TOUR_STEPS: readonly ForjaTourStep[] = [
  {
    id: "bienvenida",
    eyebrow: "Paso 1 de 7",
    title: "Bienvenido a La Forja",
    body: [
      "La Forja es un taller para diseñar sprints reales con disciplina doctrinal. No es un chatbot. No es un asistente. Es una herramienta de trabajo.",
      "Aquí no escribes prompts esperando suerte. Aquí estructuras sprints, sometes decisiones a validación, y dejas trazabilidad de cada cambio.",
    ],
    highlights: ["taller", "disciplina doctrinal", "trazabilidad"],
    cta: "Continuar",
  },
  {
    id: "que-es-la-forja",
    eyebrow: "Paso 2 de 7",
    title: "Qué es y qué no es",
    body: [
      "La Forja convierte una idea cruda en un sprint canonizado. Cada sprint pasa por 8 estados, desde propuesta hasta canonización, con gates explícitos.",
      "No te promete velocidad. Te garantiza que lo que sale al otro lado tiene firma, evidencia y reversa.",
    ],
    highlights: ["8 estados", "firma, evidencia y reversa"],
    bullets: [
      "Cada sprint tiene un dueño humano. La Forja no decide, asiste.",
      "Cada cambio queda registrado. Nada se ejecuta sin huella.",
      "Cada error tiene un patch mínimo. Nada se cubre con paliativo.",
    ],
    cta: "Continuar",
  },
  {
    id: "las-4-misiones",
    eyebrow: "Paso 3 de 7",
    title: "Las 4 misiones del tutor",
    body: [
      "Cuando consultas al tutor, La Forja decide internamente qué misión activar. No es un solo modelo. Son cuatro especializadas, cada una con un cap de costo y un patrón de validación distinto.",
      "Una de ellas activa validación cruzada con un segundo modelo independiente cuando lo pides explícitamente.",
    ],
    bullets: [
      "Classifier: clasifica tu intent en milisegundos. Bajo costo, alta frecuencia.",
      "Tutor: responde con contexto del sprint activo. Optimizado para iteración.",
      "Magna validation: validación cruzada cuando dudas o pides evidencia. Solo bajo demanda.",
      "Sprint copilot: te asiste estructurando un sprint nuevo desde cero.",
    ],
    highlights: ["cap de costo", "validación cruzada"],
    cta: "Continuar",
  },
  {
    id: "sala-de-sprint",
    eyebrow: "Paso 4 de 7",
    title: "La Sala de Sprint",
    body: [
      "Aquí vive el trabajo. Cada sprint pasa por una máquina de estados estricta: proposed, drafting, review_alfredo, review_cowork, ready_to_execute, executing, merged, canonized.",
      "No puedes saltar estados. Cada transición exige condición cumplida y queda en el historial.",
    ],
    highlights: ["máquina de estados estricta", "No puedes saltar estados"],
    cta: "Continuar",
  },
  {
    id: "cap-mensual",
    eyebrow: "Paso 5 de 7",
    title: "Tu cap mensual: 50 USD",
    body: [
      "Tienes 50 USD por mes. Punto. La Forja no permite que un loop infinito o un error de cliente vacíe tu presupuesto. Cada llamada al modelo reserva costo antes de ejecutar y libera el remanente al terminar.",
      "Si el modelo lanza una excepción, el costo se revierte. Si tu pregunta se sale del cap del mes, La Forja se detiene y te avisa.",
    ],
    highlights: ["50 USD", "reserva costo antes de ejecutar", "el costo se revierte"],
    bullets: [
      "Verás el consumo en tu Dashboard, dividido por misión.",
      "El cap se reinicia el primer día de cada mes UTC.",
      "Puedes pedirle a Alfredo que te suba el cap si tu uso lo justifica.",
    ],
    cta: "Continuar",
  },
  {
    id: "magna-opt-in",
    eyebrow: "Paso 6 de 7",
    title: "Magna validation: opt-in, no automático",
    body: [
      "Por default, el tutor responde con un solo modelo. Es rápido y barato. Magna validation es opt-in, no automático.",
      "Cuando una respuesta tiene impacto real, puedes activarla. La Forja consulta un segundo modelo independiente y te muestra ambos veredictos lado a lado. Si difieren, lo sabes antes de actuar.",
    ],
    highlights: ["opt-in, no automático", "ambos veredictos lado a lado"],
    cta: "Continuar",
  },
  {
    id: "empezar",
    eyebrow: "Paso 7 de 7",
    title: "Listo para forjar",
    body: [
      "Acabas de ver la base. El resto se aprende usando.",
      "Tu primer sprint puede ser cualquier cosa: una decisión técnica, un texto que necesitas defender, un proceso que quieres formalizar. Lo importante es someterlo a la máquina.",
    ],
    bullets: [
      "Empezar un sprint es el botón principal de tu Dashboard.",
      "Si te atoras, regresas a este tour desde el menú.",
      "Si encuentras un fallo, repórtalo. La Forja se mejora con tu evidencia, no con tu paciencia.",
    ],
    cta: "Entrar a la Forja",
  },
] as const;

export const FORJA_TOUR_STEP_COUNT = FORJA_TOUR_STEPS.length;

/**
 * Lista literal de los 8 estados del sprint que el tour menciona en
 * el paso `sala-de-sprint`. Se exporta para que el test de contrato
 * verifique sin ambigüedad que coincide exactamente con
 * `SPRINT_STATES` del backend (`apps/la-forja/api/src/routes/sprints.ts`).
 *
 * Hardening Perplexity F-D3.1-13: si esta lista derive en el futuro,
 * el test de contrato falla y bloquea el merge antes de que el copy
 * del tour mienta al usuario.
 */
export const FORJA_TOUR_SPRINT_STATES_LITERAL = [
  "proposed",
  "drafting",
  "review_alfredo",
  "review_cowork",
  "ready_to_execute",
  "executing",
  "merged",
  "canonized",
] as const;
