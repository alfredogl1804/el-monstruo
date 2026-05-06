# Herramientas para Crisis — DeepSeek

# Análisis Estratégico: Maximización del Plan de Crisis con Inventario Disponible

## 1. HERRAMIENTAS DE ALTO IMPACTO (12 herramientas críticas)

### **Perplexity Sonar** - IMPACTO: ALTO
- **Qué haría:** Monitoreo en tiempo real de narrativas emergentes en medios digitales y tradicionales sobre Clara Rosales, Carlos Koyoc Uribe, y la iniciativa de VIH. Identificar medios/periodistas clave que están impulsando la crisis.
- **Fase:** Monitoreo continuo (todas las fases, especialmente 0-6h y 24-72h)
- **Integración operativa:** Configurar alertas por palabras clave ("Clara Rosales narcotráfico", "Koyoc Uribe", "VIH Yucatán") con análisis horario enviado a Google Sheets para dashboard en tiempo real.
- **Impacto:** Alto - permite ajustar mensajes en tiempo real según la evolución mediática.

### **HeyGen** - IMPACTO: ALTO
- **Qué haría:** Crear video de respuesta inmediata de Clara (avatar si no hay video real disponible en 3h) con mensaje cuidadosamente scripteado. Luego videos cortos para redes sociales desmintiendo puntos específicos.
- **Fase:** Respuesta inmediata (0-6h) y Contraataque (Día 3-7)
- **Integración operativa:** Script escrito por GPT-5.4 → revisado por equipo legal → generación en HeyGen → publicación coordinada en Instagram/redes.
- **Impacto:** Alto - respuesta visual profesional en ventana crítica cuando producción tradicional sería lenta.

### **GPT-5.4** - IMPACTO: ALTO
- **Qué haría:** Redacción de todos los documentos del plan: comunicado de prensa, carta abierta, guiones para rueda de prensa, respuestas Q&A, análisis de riesgo de cada mensaje.
- **Fase:** Todas, especialmente 0-6h y 24-72h
- **Integración operativa:** Orquestador central que procesa inputs de Perplexity y genera outputs para otras herramientas (HeyGen, Gmail, Docs).
- **Impacto:** Alto - coherencia narrativa y velocidad de producción de contenido.

### **Mentionlytics** - IMPACTO: ALTO
- **Qué haría:** Social listening específico en Yucatán (redes, foros locales, grupos de WhatsApp detectables) para medir impacto real en electorado vs. burbuja mediática nacional.
- **Fase:** Monitoreo continuo
- **Integración operativa:** Dashboard en Google Sheets con métricas de sentimiento por región/distrito, integrado con Zapier para alertas de picos negativos.
- **Impacto:** Alto - diferencia entre reacción mediática y percepción ciudadana real.

### **Claude Opus 4.6** - IMPACTO: MEDIO-ALTO
- **Qué haría:** Análisis profundo de las acusaciones legales, identificación de contradicciones en los cargos, preparación de argumentos técnicos para la denuncia legal.
- **Fase:** Plan táctico (24-72h) especialmente para componente legal
- **Integración operativa:** Analizar documentos legales subidos via manus-upload-file, producir análisis de 10-15 páginas para abogados.
- **Impacto:** Medio-Alto - fortalece el componente jurídico de la defensa.

### **Google Workspace (Docs/Sheets/Slides)** - IMPACTO: ALTO
- **Qué haría:** War room colaborativo: Docs para comunicados, Sheets para dashboard de crisis, Slides para presentaciones internas y ruedas de prensa.
- **Fase:** Todas
- **Integración operativa:** Hub central del equipo de crisis con acceso controlado, versionado en tiempo real.
- **Impacto:** Alto - coordinación operativa esencial.

### **Zapier** - IMPACTO: ALTO
- **Qué haría:** Automatizar flujos: cuando Perplexity detecta nuevo medio importante → alerta a Slack/email → GPT-5.4 genera posible respuesta → revisión humana.
- **Fase:** Todas, especialmente monitoreo continuo
- **Integración operativa:** Conector entre todas las herramientas no nativamente integradas.
- **Impacto:** Alto - reduce tiempo de reacción de horas a minutos.

### **Instagram API** - IMPACTO: MEDIO-ALTO
- **Qué haría:** Publicación automatizada de contenido de respuesta, monitoreo de comentarios, identificación de trolls coordinados.
- **Fase:** Respuesta inmediata y Reencuadre
- **Integración operativa:** Programar publicación de videos de HeyGen, Stories con mensajes clave, respuestas a comentarios estratégicos.
- **Impacto:** Medio-Alto - canal directo con electorado más joven.

### **Together AI (FLUX)** - IMPACTO: MEDIO
- **Qué haría:** Generar imágenes para infografías que explican: 1) la falsedad de los vínculos, 2) los beneficios de la iniciativa de VIH, 3) línea de tiempo de ataques políticos.
- **Fase:** Plan táctico (24-72h) y Reencuadre
- **Integración operativa:** Prompt engineering por GPT-5.4 → generación de imágenes → aprobación → publicación en redes.
- **Impacto:** Medio - contenido visual shareable que simplifica mensajes complejos.

### **Gmail API** - IMPACTO: MEDIO
- **Qué haría:** Envío masivo pero segmentado de comunicados a: 1) medios clave, 2) aliados políticos, 3) organizaciones civiles, 4) líderes de opinión.
- **Fase:** Respuesta inmediata (0-6h)
- **Integración operativa:** Integración con Google Sheets (lista de contactos) + GPT-5.4 (personalización de mensajes por segmento).
- **Impacto:** Medio - asegura que el mensaje correcto llegue a cada audiencia.

### **SecurityTrails** - IMPACTO: MEDIO
- **Qué haría:** Investigar dominios/medios digitales que están publicando los ataques más virulentos, identificar patrones de coordinación.
- **Fase:** Contraataque (Día 3-7)
- **Integración operativa:** Análisis de dominios que publican primero las acusaciones, identificación de posibles granjas de bots/medios fantasma.
- **Impacto:** Medio - podría revelar coordinación detrás de los ataques.

### **Notion MCP** - IMPACTO: MEDIO
- **Qué haría:** Base de conocimiento centralizada de la crisis: timeline, actores clave, narrativas, lecciones aprendidas.
- **Fase:** Todas, especialmente para documentación posterior
- **Integración operativa:** Sincronización automática de insights de otras herramientas.
- **Impacto:** Medio - organización del conocimiento para futuras crisis.

## 2. CADENA DE EJECUCIÓN AUTOMATIZADA ("Sistema de Guerra YAXCHÉ")

```
FLUJO PRINCIPAL DE DETECCIÓN-RESPUESTA:
1. Perplexity Sonar → Monitoreo 24/7 de 50+ palabras clave
   ↓ (via Zapier webhook)
2. Google Sheets → Dashboard actualizado cada 15 minutos
   ↓ (automático)
3. GPT-5.4 → Análisis horario: "Tendencias, nuevos medios, narrativas emergentes"
   ↓ (via Zapier)
4. Alertas prioritarias:
   - Nivel ROJO → Slack/WhatsApp equipo + Claude Opus para análisis legal
   - Nivel NARANJA → GPT-5.4 genera borrador respuesta
   - Nivel AMARILLO → Solo registro en Sheets

FLUJO DE CONTENIDO RÁPIDO:
1. GPT-5.4 + Claude Opus → Crean mensaje central y variantes
   ↓
2. HeyGen → Genera video de Clara (3 versiones: 30s, 2min, 5min)
   ↓
3. Together AI → Crea imágenes complementarias
   ↓
4. Zapier → Publicación coordinada:
   - Instagram (video corto + imágenes)
   - Gmail (comunicado a medios)
   - Google Docs (versión completa para web)

FLUJO DE CONTRAATAQUE INTELIGENTE:
1. SecurityTrails + Perplexity → Identifican orígenes de ataques
   ↓
2. Grok 4.20 → Brainstorming de ángulos de contraataque no obvios
   ↓
3. GPT-5.4 → Convierte mejores ideas en narrativas listas
   ↓
4. Equipo humano → Decide cuándo/quién ejecuta (vía terceros)
```

## 3. HERRAMIENTAS SUBUTILIZADAS (Ventajas inesperadas)

### **Grok 4.20** - PARA PENSAMIENTO LATERAL
- **Uso inesperado:** Analizar la crisis desde ángulos no políticos: "¿Cómo resolvería esto un ingeniero de sistemas? ¿Un psicólogo? ¿Un director de cine?"
- **Ventaja:** Podría identificar narrativas de contraataque que el equipo político tradicional no vería. Ejemplo: enmarcar la crisis como "ataque misógino a mujer política fuerte" o "sabotaje a políticas de salud pública".

### **manus-analyze-video** - PARA ANÁLISIS DE OPONENTES
- **Uso inesperado:** Analizar videos de ruedas de prensa de opositores, detectar patrones en lenguaje no verbal, contradicciones entre discursos.
- **Ventaja:** Identificar debilidades en los ataques para contraargumentar específicamente.

### **Replicate** (modelos ML diversos)
- **Uso inesperado:** Usar modelos de análisis de sentimiento específicos para español yucateco (si disponibles), detectar sarcasmo/ironía en comentarios.
- **Ventaja:** Entender matices culturales locales en la recepción de la crisis.

## 4. STACK MÍNIMO VIABLE (5 herramientas)

1. **GPT-5.4** - Cerebro central para toda generación de contenido y análisis
2. **Perplexity Sonar** - Oídos para escuchar la crisis en tiempo real
3. **HeyGen** - Boca para responder visualmente con velocidad
4. **Google Sheets/Docs** - Columna vertebral para coordinación del equipo
5. **Zapier** - Sistema nervioso para conectar todo lo anterior

**Por qué:** Con estas 5 cubres: inteligencia (GPT-5.4), monitoreo (Perplexity), respuesta rápida (HeyGen), coordinación (Google Workspace), y automatización (Zapier). Es el sistema más lean que puede escalar.

## 5. RIESGOS DE USO (Herramientas problemáticas)

### **NO USAR: ElevenLabs para clonar voz de Clara**
- **Riesgo:** Si se descubre que se usó voz clonada en comunicados, sería catastrófico ("ni siquiera habla ella, es IA"). Crisis de autenticidad.
- **Alternativa:** Solo para voces de narradores en videos explicativos, nunca la voz de Clara.

### **CAUTELA EXTREMA: Grok 4.20 para mensajes finales**
- **Riesgo:** Su pensamiento "lateral" podría sugerir tácticas demasiado arriesgadas o éticamente cuestionables.
- **Mitigación:** Usar solo para brainstorming, nunca para contenido final sin filtro humano estricto.

### **LIMITAR: Together AI/Novita AI para imágenes de Clara**
- **Riesgo:** Generar imágenes falsas de Clara en contextos que podrían ser malinterpretados o usados en su contra.
- **Mitigación:** Solo para gráficos informativos, nunca imágenes realistas de personas.

### **IRRELEVANTES PARA ESTA CRISIS:**
- **Fashn AI** (virtual try-on ropa) - cero aplicación
- **Meshy AI** (3D) - a menos que quieras hacer un modelo 3D de la "torre de mentiras" de los opositores (riesgo de parecer frívolo)
- **Keepa/Best Buy** - tracking de precios no aplica
- **PayPal/RevenueCat** - componentes comerciales no relevantes en crisis política

---

## **RECOMENDACIÓN OPERATIVA INMEDIATA (Primeras 6 horas):**

1. **Configurar YA:** Perplexity + Google Sheets dashboard con palabras clave críticas
2. **Ejecutar simultáneamente:**
   - GPT-5.4: Redactar comunicado de prensa y guion para video
   - Claude Opus: Analizar implicaciones legales de las acusaciones
   - HeyGen: Producir video de Clara (si hay material real, solo editar; si no, avatar profesional)
3. **Automatizar con Zapier:** Flujo de alertas para cuando medios nacionales empiecen a cubrir
4. **Preparar contraataque:** SecurityTrails investigando medios que publican primero + Grok 4.20 buscando ángulos creativos

**Regla de oro:** Todas las herramientas deben servir a la narrativa central: "Clara Rosales es víctima de un ataque político coordinado para detener sus avances en salud pública (VIH)." La tecnología acelera y potencia, pero no reemplaza la coherencia del mensaje político.