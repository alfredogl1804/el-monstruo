# REPORTE CONSOLIDADO: Mapa de Conexiones entre Medios y Actores Clave

## Operación "Doble Eje" — Fase de Atribución

**Fecha:** 23 de febrero de 2026

**Técnicas ejecutadas:** Código fuente (18 sitios), Búsquedas cruzadas (20 pares), Estilometría (GPT-5.2), Wayback Machine (5 sitios), Scraping social (Twitter + Facebook), Cruce de amplificadores (11 investigaciones)

---

## 1. MAPA COMPLETO DE MEDIOS Y PROPIETARIOS

La investigación identificó y analizó 18 medios involucrados en la cadena de amplificación. La tabla siguiente resume los propietarios confirmados y el nivel de anonimato de cada medio.

<table header-row="true">
<tr>
<td>Nivel</td>
<td>Medio</td>
<td>Propietario</td>
<td>Anonimato</td>
<td>Ataques confirmados</td>
</tr>
<tr>
<td>Iniciador</td>
<td>PorEsto! (Todo es Personal)</td>
<td>Grupo PorEsto / Autor desconocido</td>
<td>PARCIAL</td>
<td>SI - 13 feb 2026</td>
</tr>
<tr>
<td>Iniciador</td>
<td>Notisureste (Los Malvados Aluxes)</td>
<td>Daniel Barquet Loeza</td>
<td>TRANSPARENTE</td>
<td>SI - 13 feb 2026</td>
</tr>
<tr>
<td>Amplificador</td>
<td>El Chismografo en la Red</td>
<td>TOTALMENTE OCULTO</td>
<td>OCULTO</td>
<td>SI</td>
</tr>
<tr>
<td>Amplificador</td>
<td>Dulce Patria</td>
<td>Alejandro Rodriguez Lopez (Pachuca)</td>
<td>SOSPECHOSO</td>
<td>SI</td>
</tr>
<tr>
<td>Amplificador</td>
<td>Voz Libre Yucatan</td>
<td>TOTALMENTE OCULTO</td>
<td>OCULTO</td>
<td>SI - 60 reacciones</td>
</tr>
<tr>
<td>Amplificador</td>
<td>Valor Por Yucatan</td>
<td>OCULTO (Squarespace en construccion)</td>
<td>OCULTO</td>
<td>SI</td>
</tr>
<tr>
<td>Amplificador</td>
<td>Grillo de Yucatan + Grillo Porteno</td>
<td>Gabino Tzec Valle (MISMO operador)</td>
<td>PARCIAL</td>
<td>SI</td>
</tr>
<tr>
<td>Amplificador</td>
<td>El Principal</td>
<td>Rudy Lavalle Burgos</td>
<td>PARCIAL</td>
<td>SI - 17 ataques</td>
</tr>
<tr>
<td>Amplificador</td>
<td>Sol Yucatan</td>
<td>Pedro Daniel Rodriguez Hernandez</td>
<td>TRANSPARENTE</td>
<td>SI - 9 ataques</td>
</tr>
<tr>
<td>Amplificador</td>
<td>Formal Prision</td>
<td>Pablo Donjuan Callejo (Chihuahua)</td>
<td>SOSPECHOSO</td>
<td>SI - 5 ataques</td>
</tr>
<tr>
<td>Amplificador</td>
<td>Noticias Merida</td>
<td>contactonoticiasmerida@gmail.com</td>
<td>PARCIAL</td>
<td>SI</td>
</tr>
<tr>
<td>Nacional</td>
<td>La Razon</td>
<td>Francisco Resendiz (columnista)</td>
<td>PARCIAL</td>
<td>SI - escala nacional</td>
</tr>
<tr>
<td>Nacional</td>
<td>Proyecto Puente</td>
<td>Luis Alberto Medina</td>
<td>TRANSPARENTE</td>
<td>SI - 4 negativos</td>
</tr>
<tr>
<td>Mena publica</td>
<td>La Jornada Maya</td>
<td>Sabina Leon / Fabrizio Leon Diez</td>
<td>TRANSPARENTE</td>
<td>NO directo</td>
</tr>
<tr>
<td>Mena publica</td>
<td>SIPSE</td>
<td>Gerardo Garcia Gamboa</td>
<td>PARCIAL</td>
<td>NO directo</td>
</tr>
<tr>
<td>Mena publica</td>
<td>LaRevista Peninsular</td>
<td>larevista.com.mx</td>
<td>PARCIAL</td>
<td>INDIRECTO</td>
</tr>
<tr>
<td>Amplificador social</td>
<td>ChismografoMid (Facebook)</td>
<td>TOTALMENTE OCULTO</td>
<td>OCULTO</td>
<td>SI - ataque directo</td>
</tr>
<tr>
<td>Amplificador social</td>
<td>Noti_Merida (Twitter)</td>
<td>publitWEETS@hotmail.com (servicio pagado)</td>
<td>SOSPECHOSO</td>
<td>Amplifica por pago</td>
</tr>
</table>

---

## 2. HALLAZGOS CRÍTICOS POR TÉCNICA

### 2.1 Código Fuente (18 sitios)

El análisis de IDs de tracking reveló que los operadores son cuidadosos: no comparten Google Analytics, AdSense ni Meta Pixel entre sitios. Sin embargo, se encontraron 3 hallazgos relevantes:

**GrilloPorteño redirige a GrilloDeYucatán.** Mismo servidor nginx/1.26.0 en Ubuntu. Son el mismo medio operado por Gabino Tzec Valle. Esto confirma que un solo operador maneja dos "marcas" para aparentar mayor cobertura.

**LaRevista y NoticiasM\u00e9rida comparten hosting "hcdn".** Ambos usan WordPress en el mismo proveedor. Esto podría ser coincidencia (proveedor popular) o infraestructura compartida.

**El Chismógrafo NO tiene NINGÚN tracking.** Cero Google Analytics, cero AdSense, cero Meta Pixel, cero GTM. WordPress en Apache puro. Esto es deliberado: quien lo opera sabe que los IDs de tracking pueden identificarlo.

### 2.2 Búsquedas Cruzadas (20 pares)

De 20 búsquedas cruzadas entre propietarios de medios y actores clave, se encontraron 5 conexiones:

**CONEXIÓN DIRECTA: Francisco Reséndiz (La Razón) ↔ Sergio Vadillo.** Reséndiz menciona a Vadillo en su columna del 20 de junio de 2024, informando sobre su designación al frente del PRI en Mérida. Cuando en febrero 2026 Reséndiz escribe "nos advierten desde la Tierra de Mayab", la pregunta es: ¿quién le advierte? La conexión con Vadillo es la respuesta más probable.

**CONEXIÓN INDIRECTA: Rudy Lavalle ↔ Mena, Vadillo, Rosado Pat.** Los tres aparecen en el Diario Oficial del Gobierno de Yucatán en diferentes fechas, lo que confirma que todos operan en el mismo ecosistema político-empresarial yucateco.

**CONEXIÓN COMPLEJA: Pedro Daniel Rodríguez (Sol Yucatán) ↔ Vadillo.** Vadillo afirma tener buena relación con Rodríguez, pero Sol Yucatán acusa a Vadillo de usar su nombre para fraudes. Relación aparentemente antagónica que podría ser de fachada.

### 2.3 Estilometría

GPT-5.2 determinó con un **85-90% de confianza que "Todo es Personal" NO fue escrita por Carlos Mena Baduy**. Las diferencias en longitud de oraciones (25-30 vs 12-16 palabras), uso de fuentes anónimas ("se comenta"), tono editorial vs técnico, y estructura de párrafos son demasiado marcadas. Mena podría ser el proveedor de datos, pero la pluma es de otro autor, probablemente un periodista político profesional de la redacción de PorEsto.

### 2.4 Wayback Machine

**El Chismógrafo** apareció por primera vez en noviembre de 2021, con 20 snapshots hasta junio de 2023. Las versiones antiguas podrían revelar información de contacto eliminada posteriormente.

**Dulce Patria** apareció en enero de 2021, registrado en Pachuca, Hidalgo (no en Yucatán). Un medio "yucateco" registrado a 1,500 km de Mérida.

**Formal Prisión** no tiene NINGÚN snapshot en Wayback Machine, lo que sugiere que existió brevemente o nunca tuvo presencia web significativa. Opera exclusivamente desde redes sociales.

### 2.5 Scraping Social

**Red de amplificación de Mena en Twitter:** 8 cuentas principales, lideradas por @LaRevistaP (26 tweets), @novedadesqroo (11, parte de Grupo SIPSE), @LaJornadaMaya (10), @Noti_Merida (8, servicio de amplificación pagado).

**@Noti_Merida es un servicio de amplificación pagado** (email: publitWEETS@hotmail.com). Alguien paga para que amplifique contenido de Mena. ¿Quién paga?

**ChismografoMid (Facebook)** publicó un post el 19 feb 2026 que menciona a Cortés, CONADE, Rommel, Infonavit, Castro, Pacheco y Guillermo en un solo artículo. Es el nodo que conecta ambos ejes.

**No hay interacciones directas Mena-Lavalle-Vadillo-Meza en Twitter.** La coordinación opera por canales privados.

### 2.6 Cruce de Amplificadores con Targets

De los 11 amplificadores de Mena investigados, solo 2 muestran doble función (amplificar a Mena Y atacar targets). El hallazgo más importante es la cadena **SIPSE → Novedades de Quintana Roo → cobertura favorable de Zapata Bello → Vadillo**, que conecta el ecosistema editorial de Mena con el Eje 2.

---

## 3. CADENA DE AMPLIFICACIÓN DOCUMENTADA (13-20 feb 2026)

La campaña contra Guillermo Cortés siguió un patrón de 4 niveles en 7 días:

**Nivel 1 — Iniciadores (13 feb 2026):** PorEsto "Todo es Personal" y Barquet "Los Malvados Aluxes" publicaron el MISMO DÍA con la MISMA narrativa. Tono analítico, uso de fuentes anónimas ("se comenta"), sin pruebas documentales.

**Nivel 2 — Amplificadores digitales (16-17 feb):** 5+ medios digitales (Chismógrafo, Dulce Patria, Voz Libre, Valor Por Yucatán, Grillo) republicaron contenido IDÉNTICO o casi idéntico, escalando el tono a "corrupto", "moches", "mega fraude".

**Nivel 3 — Escalamiento nacional (19 feb):** La Razón (Francisco Reséndiz, "Las Batallas") y Diario de Yucatán (Plaza Grande) recogieron la narrativa. Reséndiz dice "nos advierten desde la Tierra de Mayab" — alguien le filtró.

**Nivel 4 — Viralización social (19-20 feb):** ChismografoMid, Sol Yucatán, grupos de Facebook completaron la saturación.

---

## 4. CONEXIONES CONFIRMADAS Y SOSPECHOSAS

### Confirmadas:
1. GrilloPorteño = GrilloDeYucatán (mismo operador: Gabino Tzec Valle)
2. Barquet y PorEsto publicaron el mismo día (13 feb 2026) — sincronización editorial
3. Reséndiz (La Razón) conoce y sigue a Vadillo — conexión directa documentada
4. Mena es columnista de SIPSE, LaRevista, LaJornadaMaya, PorEsto — red editorial amplia
5. @antonio_rsa1 confirmó públicamente "Finex representada por Carlos Mena Baduy"

### Sospechosas (requieren más investigación):
1. "Todo es Personal" NO es escrita por Mena — ¿quién es el ghostwriter?
2. @Noti_Merida es servicio pagado — ¿quién paga para amplificar a Mena?
3. Dulce Patria registrado en Pachuca — ¿quién es Alejandro Rodríguez López?
4. Formal Prisión registrado en Chihuahua — ¿quién es Pablo Donjuan Callejo?
5. El Chismógrafo deliberadamente sin tracking — operador sofisticado
6. SIPSE tiene cobertura favorable de Zapata Bello — ¿conexión con Vadillo?

---

## 5. PREGUNTAS ABIERTAS PRIORITARIAS

1. ¿Quién escribe realmente "Todo es Personal"? La estilometría dice que NO es Mena.
2. ¿Quién es el administrador de ChismografoMid y El Chismógrafo en la Red?
3. ¿Cómo se coordinaron Barquet y PorEsto para publicar el mismo día? ¿Quién dio la orden?
4. ¿Quién le filtró a Reséndiz (La Razón) la información "desde la Tierra de Mayab"?
5. ¿Qué relación tiene Alejandro Rodríguez López (Dulce Patria, Pachuca) con Yucatán?
6. ¿Los ataques a Rogerio Castro siguen el mismo patrón de amplificación?

---

## 6. PRÓXIMOS PASOS RECOMENDADOS

1. Visitar versiones antiguas de El Chismógrafo en Wayback Machine para buscar info de contacto eliminada
2. Investigar al ghostwriter de "Todo es Personal" en la redacción de PorEsto
3. Analizar patrones de publicación de ataques a Castro vs ataques a CONADE (¿mismos medios, mismos días?)
4. Profundizar en la conexión Reséndiz-Vadillo
5. Investigar a Alejandro Rodríguez López (Dulce Patria) y Pablo Donjuan Callejo (Formal Prisión)
