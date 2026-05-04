# [Hilo Manus Catastro] · Tarea P3: Drafting Tests Sprint 85
**Fecha:** 2026-05-04
**Objetivo:** Definir los tests de aceptación con criterios medibles para el Sprint 85 (Critic Visual + Product Architect) ANTES de escribir el código.

## Test 1 v2: Landing Curso Pintura al Óleo

**Contexto:** Mismo prompt que falló en Sprint 84.1.
**Prompt Usuario:** "Quiero una landing page para mi curso presencial de pintura al óleo en Mérida. El maestro se llama Carlos y cuesta $4,990 MXN."

### 1.1 Expected Output del Product Architect (`brief.json`)
*   `vertical`: "education_arts"
*   `client_brand.personality`: "warm", "evocative"
*   `client_brand.color_palette_hint`: debe incluir tonos cálidos (terracota, ocre, crema).
*   `client_brand.typography_hint`: "serif" (para headlines).
*   `structure.sections_required`: ["hero", "instructor", "curriculum", "pricing", "testimonials", "faq", "footer"] (mínimo 5).
*   `data_known.instructor_name`: "Carlos"
*   `data_known.price`: "$4,990 MXN"
*   `data_missing`: ["duration", "location_details", "dates"] (esperado que falten datos).
*   `user_question_emitted`: Debe haber UNA pregunta consolidada pidiendo fechas, duración y dirección exacta.

### 1.2 Criterios de Aceptación del Critic Visual (Rúbrica)
Para que el deploy pase (`quality_passed=true`, score >= 80), el screenshot debe cumplir:

| Componente | Peso Max | Criterio Medible (Pass = 100% del peso) |
| :--- | :--- | :--- |
| **Estructura** | 20 | Renderiza hero, instructor, pricing, footer. |
| **Contenido** | 25 | Nombre "Carlos" y precio "$4,990 MXN" visibles. Cero "Lorem Ipsum". Si el usuario ignoró la pregunta consolidada, los placeholders `<<FECHAS>>` o `<<DURACIÓN>>` deben ser visibles y obvios (no inventados). |
| **Visual** | 15 | Hero image presente (generada vía Replicate/Recraft). Texto sobre hero legible (contraste WCAG AA). |
| **Brand Fit** | 15 | Usa tipografía serif en títulos. Colores cálidos (no azul corporativo ni gris tech). |
| **Mobile** | 10 | Layout responsive a 375px (sin overflow horizontal). |
| **Performance**| 5 | LCP < 2.5s (medido sintéticamente). |
| **CTA** | 5 | Botón "Inscribirse" o similar visible above-the-fold. |
| **Meta tags** | 5 | `<title>` y `<meta name="description">` presentes y relevantes. |

**Expected Result:** El Executor generará una primera versión que probablemente falle en Contenido (inventará datos) o Brand Fit (usará colores genéricos). El Critic Visual debe detectarlo, asignar score < 80, y obligar al Executor a corregir. Al iteración 2 o 3, debe pasar.

---

## Test 2 v2: Marketplace Tutorías Matemáticas

**Contexto:** Backend + Frontend para un marketplace de servicios.
**Prompt Usuario:** "Necesito una plataforma donde estudiantes puedan buscar y reservar tutorías de matemáticas con diferentes profesores. Que se vea moderna."

### 2.1 Expected Output del Product Architect (`brief.json`)
*   `vertical`: "marketplace_services"
*   `product_meta.product_type`: "webapp"
*   `structure.sections_required`: ["hero_search", "tutor_grid", "tutor_profile_modal", "booking_flow"]
*   `data_missing`: ["pricing_model", "payment_gateway", "tutor_vetting_process"]
*   `user_question_emitted`: Pregunta sobre si la plataforma cobra comisión y cómo se paga.

### 2.2 Criterios de Aceptación Backend (Data Integrity Check)
Este test valida la capacidad de generar un backend funcional y seedearlo correctamente.

1.  **Endpoints Esperados:**
    *   `GET /api/tutores`: Retorna array de objetos tutor.
    *   `GET /api/tutores/{id}`: Retorna detalle de tutor.
    *   `POST /api/reservar`: Acepta payload `{tutor_id, date, student_email}` y retorna `201 Created`.
2.  **Seed Data Plausible:**
    *   La base de datos (SQLite en memoria o Supabase temporal) debe inicializarse con al menos 3 tutores.
    *   **NO DEBE HABER:** "Tutor 1", "Tutor 2".
    *   **DEBE HABER:** Nombres plausibles ("Ana López", "Roberto Sánchez"), materias específicas ("Cálculo Vectorial", "Álgebra Lineal"), precios plausibles ($250-$500 MXN/hr).
3.  **Cobertura de Tests:** El código generado debe incluir tests unitarios básicos (pytest/jest) que pasen exitosamente durante el CI/CD pipeline interno antes del deploy.

### 2.3 Criterios de Aceptación Critic Visual (Rúbrica)
*   **Estructura (20):** Grid de tutores visible con al menos 3 tarjetas.
*   **Visual (15):** Fotos de perfil de tutores generadas/placeholders coherentes (no broken links).
*   **Brand Fit (15):** Diseño "moderno" (sans-serif, UI limpia, estilo SaaS).

---

## Test 3: Auto-replicación con Producto Real (Test de Humo Final)

**Contexto:** Validar que el Monstruo puede generar valor comercial real.
**Producto Candidato:** "Landing page para un despacho de abogados corporativos en CDMX especializado en nearshoring."

### 3.1 Criterio de Éxito Binario
1.  El sistema completa el pipeline (Architect -> Planner -> Executor <-> Critic) sin intervención humana.
2.  Despliega la URL final.
3.  **Juicio Humano (Alfredo):** Abre la URL y dictamina "Sí, es comercializable" (puedo venderla por $30K-$50K MXN con ajustes mínimos).

### 3.2 Checklist de Quality Gates (Automatizado)
*   [ ] `brief.json` generado con vertical `professional_services`.
*   [ ] Hero image generada representa un entorno corporativo moderno/CDMX.
*   [ ] Copywriting utiliza tono formal, experto y persuasivo.
*   [ ] Formulario de contacto funcional (UI).
*   [ ] Critic Score >= 85 en la última iteración.

---
**Resumen de Métricas de Éxito del Sprint 85:**
Para declarar el Sprint 85 cerrado y verde:
1. Mínimo 2 de los 3 tests deben completar el deploy con `quality_passed=true`.
2. El Critic Visual debe haber demostrado rechazar (score < 80) al menos 1 iteración defectuosa del Executor en los logs.
3. El Test 3 debe obtener el veredicto positivo de Alfredo.
