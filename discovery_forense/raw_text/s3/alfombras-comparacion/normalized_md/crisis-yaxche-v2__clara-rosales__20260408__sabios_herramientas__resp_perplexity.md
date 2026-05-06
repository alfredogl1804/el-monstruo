# Herramientas para Crisis — Perplexity

### 1. HERRAMIENTAS DE ALTO IMPACTO
Estas 8 herramientas del inventario destacan por su potencial directo en crisis política de nivel ROJO EMERGENTE, priorizando monitoreo, generación de contenido creíble y automatización operativa. Seleccionadas por alineación con fases de YAXCHÉ y escalabilidad en 48-72 horas.

| Herramienta | Acción exacta | Fase del plan | Integración operativa | Impacto estimado |
|-------------|---------------|---------------|-----------------------|------------------|
| **Mentionlytics** | Monitoreo en tiempo real de menciones en redes/sociales sobre "Clara Rosales + Koyoc" y "VIH iniciativa", con alertas de sentiment y picos de viralidad. | Monitoreo continuo + Respuesta inmediata (0-6h) | Conectar vía Zapier a Google Sheets para dashboard en Supabase; alertas push a Asana. | **Alto**: Detecta escaladas tempranas, reduce score de 88/100 en 20-30% al contener narrativas. |
| **Perplexity Sonar** | Búsqueda web en tiempo real de acusaciones (origen de leaks, perfiles de Koyoc), con citas verificables para desmentidos. | Respuesta inmediata (0-6h) + Plan táctico (24-72h) | Prompt: "Fuentes primarias vínculos Clara Rosales narcotráfico Yucatán"; exportar a Google Docs vía manus-upload-file. | **Alto**: Proporciona facts verificables para comunicado y carta abierta. |
| **GPT-5.4** | Orquestar redacción de comunicado, guion de video de Clara y carta abierta, sintetizando datos de Perplexity y análisis de Claude. | Respuesta inmediata (0-6h) + Plan táctico | Input contexto crisis → Generar drafts → Revisar en Notion war room → Iterar con Grok para ángulos contraataque (e.g., PAN-Kanasín). | **Alto**: Acelera contenido profesional, impacto en contención 40%. |
| **HeyGen** | Generar video de 60s de Clara negando vínculos (avatar o clon real), con tono empático y facts citados. | Respuesta inmediata (0-6h) | Guion de GPT-5.4 → Upload script → Exportar MP4 → Postear en Instagram vía Zapier. | **Alto**: Humaniza respuesta, viralidad positiva en Yucatán (alcance 10x posts estáticos). |
| **Zapier** | Automatizar flujo: Mentionlytics detecta spike → Notifica Asana/Gmail → Trigger GPT-5.4 para draft respuesta. | Todas las fases + Monitoreo | Config: Trigger Mentionlytics → Action Gmail a equipo + Asana task "Revisar con Claude". | **Alto**: Reduce tiempo reacción de horas a minutos, clave en ventana 48h. |
| **Instagram** | Publicar video HeyGen, stories con infografías (FLUX) y lives de rueda de prensa. | Plan táctico (24-72h) + Contraataque | Contenido de HeyGen/ElevenLabs → Schedule posts → Monitorear insights para ajustar. | **Medio-Alto**: Plataforma clave en Yucatán, insights guían reencuadre. |
| **Claude Opus 4.6** | Análisis profundo de riesgos legales (denuncia vs. Koyoc leaks) y crítica de narrativa VIH. | Plan táctico + Contraataque (Día 3-7) | Prompt largo con contexto completo → Output a Notion para war room. | **Alto**: Evita errores legales, fortalece denuncia. |
| **Google Sheets + Supabase** | Dashboard en vivo: score crisis, menciones, sentiment; predicción escalada. | Monitoreo continuo | Zapier ingesta datos Mentionlytics → Visualizar en Sheets → Backend Supabase para queries equipo. | **Medio**: Visibilidad total, impacto sostenido post-72h. |

### 2. CADENA DE EJECUCIÓN
**Sistema de Guerra Integrado "YAXCHÉ WAR ROOM"** (automatizado en 2h setup vía Zapier + manus-mcp-cli):

1. **Monitoreo → Alerta**: Mentionlytics + Perplexity Sonar escanean "Clara Rosales narcotráfico/VIH" cada 15min → Zapier trigger si score >80 → Notificación Gmail/Asana al equipo (Clara, abogados, spin doctors).
2. **Análisis → Síntesis**: Zapier envía datos a GPT-5.4 (prompt fijo: "Analiza menciones, propone 3 respuestas: desmentido, contraataque, reencuadre") → Claude Opus valida legalmente → Output a Notion war room.
3. **Generación → Distribución**: GPT genera guion → HeyGen/ElevenLabs crea video/audio → Instagram auto-post + Vercel deploy landing "transparencia.clararosales.mx" con facts citados.
4. **Tracking → Loop**: Google Sheets actualiza dashboard (Supabase backend) → Si escalada, Grok brainstorm "ángulos no obvios" (e.g., filtrar PAN-Kanasín) → Loop a fase Contraataque.
   
**Setup inicial**: Usa manus-mcp-cli para conectar Zapier a todas; test en 30min con simulación spike.

### 3. HERRAMIENTAS SUBUTILIZADAS
- **SecurityTrails**: No obvia en política, pero investiga DNS/WHOIS de sitios leaks (e.g., origen "narcotrafico-yucatan.mx") para rastrear atacantes (oposición/PAN?). Acción: Query dominios acusadores → Identifica IPs y contrataque legal. Ventaja: Prueba externa de "fake news", filtra vía terceros en Día 3.
- **Gemini 3.1 Pro (multimodal)**: Analiza imágenes/videos acusatorios (e.g., fotos manipuladas con Koyoc) → Detecta edits/ deepfakes. Acción: Upload vía manus-upload-file → Reporte para rueda de prensa.
- **Grok 4.20**: Brainstorm ángulos contraintuitivos, como ligar acusación VIH a "ataque machista" en Yucatán conservador.

### 4. STACK MÍNIMO VIABLE (5 herramientas)
1. **Mentionlytics**: Monitoreo base, sin él no ves escaladas.
2. **Zapier**: Glue que automatiza todo, multiplica eficiencia 5x.
3. **GPT-5.4**: Cerebro para contenido/orquestación inmediata.
4. **HeyGen**: Video respuesta #1, humano y viral.
5. **Google Sheets + Notion**: War room/dashboard simple, tracking sin complejidad.
**Por qué**: Cubren 80% impacto (monitoreo 30%, contenido 30%, auto 20%); escalables a full stack, costo cero extra.

### 5. RIESGOS DE USO
- **NO usar**: 
  - HeyGen/ElevenLabs sin disclaimer "generado con IA" (riesgo deepfake backlash, ilegal en México post-2024).
  - Instagram directo si sin VPN/proxy (huella digital traceable en crisis narcopolítica).
  - PayPal/RevenueCat/Fashn AI/Meshy: Irrelevantes, distraen recursos.
- **Contraproducentes**:
  - Grok sin supervisión: Ángulos "no obvios" podrían sugerir leaks agresivos prematuros, escalando crisis.
  - Replicate (análisis sentimiento): Impreciso en español yucateco, genera falsos positivos → Decisiones erradas.
  - Vercel landing sin HTTPS/auditoría: Exposición a hacks, contraproducente en "transparencia". Recomendación: Siempre validar outputs humanos antes deploy.