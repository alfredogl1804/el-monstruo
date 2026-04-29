# Stack Tecnológico y Roadmap de Construcción
**Fecha:** 7 de abril de 2026

## 1. Stack Tecnológico Propuesto

Para cumplir con la "Regla Universal" del Monstruo (no construir nada desde cero, sino conectar e integrar), el stack tecnológico se basa en plataformas robustas, escalables y con amplio soporte de APIs, priorizando soluciones "as a service" y de código abierto.

### 1.1 Infraestructura y Backend
- **BaaS (Backend as a Service):** Supabase (PostgreSQL, Auth, Storage, Edge Functions). Ofrece escalabilidad inmediata, seguridad a nivel de fila (RLS) y soporte nativo para pgvector (esencial para las funcionalidades de IA).
- **Orquestación de IA:** OpenClaw (framework de agentes) y LangGraph para flujos de trabajo complejos y toma de decisiones.
- **Motor de Pagos y KYC:** Stripe Connect (para gestión de pagos fraccionados y retenciones) integrado con un proveedor de KYC especializado en LATAM (ej. Truora o Jumio).
- **Hosting / Despliegue:** Vercel (para el frontend) y Railway o Render (para servicios de backend pesados o workers de IA).

### 1.2 Frontend (Web y Móvil)
- **Web App:** Next.js (React) con Tailwind CSS y shadcn/ui para un desarrollo rápido y una interfaz de usuario moderna y responsiva.
- **Mobile App (Fase 2):** React Native (Expo) para compartir lógica de negocio con la web app y acelerar el lanzamiento en iOS y Android.
- **Visualización Inmersiva:** Matterport o Three.js para la integración de tours virtuales 360°.

### 1.3 Herramientas de IA Integradas
- **Modelos Fundacionales:** GPT-5.4 (para razonamiento complejo y análisis de contratos), Claude 3.5 Sonnet/Opus (para generación de contenido y análisis de mercado).
- **Asistente Conversacional:** Vercel AI SDK integrado con el modelo seleccionado para el onboarding y soporte al cliente.

---

## 2. Estrategia de Crecimiento (Go-to-Market)

### Fase Inicial: "Sureste Exclusivo"
- **Foco Geográfico:** Sureste de México (alta plusvalía, proyectos turísticos e industriales).
- **Adquisición de Oferta (Lado 1):** Alianzas estratégicas con 3-5 desarrolladores locales de confianza para listar los primeros proyectos "semilla".
- **Adquisición de Demanda (Lado 2):** Campañas de marketing digital segmentadas, enfatizando la baja barrera de entrada ($10 USD) y la seguridad (Fideicomiso).
- **Estrategia FOMO:** Listar propiedades con disponibilidad limitada y cronómetros de fondeo para generar urgencia.

### Expansión: "Efecto Red"
- **Programa de Referidos:** Recompensas en saldo (ej. "$5 USD para invertir") por invitar a nuevos usuarios que completen su primera inversión.
- **Gamificación Social:** Tablas de clasificación anónimas ("Top Inversionistas del Mes") y foros de comunidad integrados en el módulo de gobernanza.
- **Apertura a Particulares:** Habilitar la funcionalidad para que dueños particulares listen sus propiedades (pagando el 25% inicial), expandiendo el inventario orgánicamente.

---

## 3. Roadmap de Construcción (Acelerado por IA)

### Sprint 1: MVP Core (Semanas 1-4)
- **Objetivo:** Plataforma web funcional para listar propiedades y procesar inversiones simuladas (Modo Papel).
- **Entregables:** Landing page, registro/login (Supabase Auth), catálogo de propiedades estático, calculadora de rendimientos básica.
- **Herramientas IA:** Cursor IDE, v0 (Vercel) para generación de UI.

### Sprint 2: Motor Transaccional y KYC (Semanas 5-8)
- **Objetivo:** Habilitar inversiones reales con dinero real.
- **Entregables:** Integración de Stripe Connect, flujo de KYC automatizado, asignación de fracciones en base de datos, panel de inversionista básico.
- **Herramientas IA:** OpenClaw para validación de documentos KYC, GPT-5.4 para redacción de términos y condiciones.

### Sprint 3: Gobernanza y Retención (Semanas 9-12)
- **Objetivo:** Implementar el modelo dual 25/75 y herramientas de engagement.
- **Entregables:** Módulo de votación para el tramo 25%, foros de discusión, sistema de notificaciones, asistente IA conversacional para onboarding.
- **Herramientas IA:** LangGraph para flujos de votación y resolución de conflictos.

### Sprint 4: Mercado Secundario y Mobile (Semanas 13-16)
- **Objetivo:** Proveer liquidez y acceso móvil.
- **Entregables:** Tablón de ofertas para compra/venta entre usuarios, lanzamiento de app móvil en versión beta.
- **Herramientas IA:** Modelos predictivos para sugerir precios en el mercado secundario.
