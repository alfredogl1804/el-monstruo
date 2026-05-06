# ANÁLISIS OSINT - CÓDIGO FUENTE DE 9 MEDIOS
# Fecha: 22 Feb 2026

---

## HALLAZGOS CRÍTICOS

### HALLAZGO 1: GRILLO DE YUCATÁN Y GRILLO PORTEÑO - MISMO OPERADOR CONFIRMADO

| Atributo | Grillo de Yucatán | Grillo Porteño |
|----------|-------------------|----------------|
| Hosting | DigitalOcean | DigitalOcean |
| Tracker | stats.wp.com | stats.wp.com |
| Autor | "Grillo Uno", "admin" | "admin", "Grillo Uno", "Jhony Alamilla Castro" |
| Theme | Newspaper | No identificado |
| Facebook | "Yucatán en Grande" | N/A |

**CONCLUSIÓN:** Son del MISMO operador. Comparten hosting (DigitalOcean), tracker (stats.wp.com), y el mismo autor seudónimo "Grillo Uno". El Grillo Porteño revela un nombre real: **Jhony Alamilla Castro**.

**HALLAZGO BOMBA: Jhony Alamilla Castro es probablemente el operador real detrás de ambos "Grillos".**

---

### HALLAZGO 2: FORMAL PRISIÓN COMPARTE CLUSTER CON LOS GRILLOS

| Atributo | Formal Prisión | Grillos |
|----------|---------------|---------|
| Hosting | DigitalOcean | DigitalOcean |
| Tracker | stats.wp.com | stats.wp.com |
| Autor | "Jose Duque", "admin" | "Grillo Uno", "admin" |

**CONCLUSIÓN:** Formal Prisión está en el mismo cluster técnico (DigitalOcean + stats.wp.com). El autor "Jose Duque" podría ser real o seudónimo. La coincidencia de infraestructura sugiere posible mismo webmaster.

---

### HALLAZGO 3: EL PRINCIPAL - OPACO Y PROFESIONAL

- Sin Google Analytics
- Sin AdSense
- Sin Facebook Pixel
- Usa reCAPTCHA (protección contra bots)
- NO es WordPress
- Sin información de contacto (solo formulario)
- Sin autores identificados

**CONCLUSIÓN:** El Principal es el más opaco de todos. No tiene NINGÚN tracker identificable. Esto es inusual para un medio de noticias y sugiere que fue diseñado específicamente para ser difícil de rastrear. Rudy Lavalle opera en la sombra.

---

### HALLAZGO 4: EL CHISMÓGRAFO - HOSTING BARATO, OPERACIÓN BÁSICA

- WordPress con tema ColorMag (tema gratuito popular)
- Google Analytics: **UA-122967539-1**
- Hosting: Unified Layer (Bluehost)
- Autor: "Chismografo"
- Sin info de contacto

**NOTA:** El ID de Analytics UA-122967539-1 es ÚNICO. Si aparece en otro sitio, confirma mismo operador.

---

### HALLAZGO 5: NOTICIAS MÉRIDA - HOSTING COMPARTIDO CON EL PRINCIPAL

| Atributo | Noticias Mérida | El Principal |
|----------|----------------|-------------|
| Hosting | Hostinger | Hostinger |
| AdSense | ca-pub-2882425394935324 | No encontrado |
| Theme | newsnow | No WordPress |
| Contacto | contactonoticiasmerida@gmail.com | Solo formulario |

**CONCLUSIÓN:** Comparten hosting (Hostinger) pero diferentes tecnologías. La cuenta de Gmail genérica sugiere operación informal.

---

### HALLAZGO 6: SOL YUCATÁN - CONEXIÓN CON QUINTANA ROO

- Dirección física: **Av. Álvaro Obregón No. 500, Chetumal, Quintana Roo 77050**
- Email: informacion@solyucatan.mx
- Teléfono: +52 999 270 7948 (prefijo 999 = Mérida, pero dirección en Chetumal)
- Columnistas: **Ricardo Ravelo** (periodista de Proceso), **Rafael Loret de Mola**, **Urbano Barrera**

**HALLAZGO BOMBA:** Sol Yucatán tiene como columnista a **Ricardo Ravelo**, quien es periodista de **Proceso**. Si Rosado Pat filtra a Proceso Y Sol Yucatán tiene columnistas de Proceso, esto podría ser un canal de distribución.

---

### HALLAZGO 7: PORESTO! - MEDIO ESTABLECIDO CON INFRAESTRUCTURA PROFESIONAL

- Empresa: **COMPAÑÍA EDITORA DEL MAYAB S.A. DE C.V.**
- GTM: GTM-WH3L8595
- Analytics: UA-172994742-1
- AdSense: ca-pub-3359897221252780
- Tracker externo: oneweather.org
- Múltiples periodistas identificados

**CONCLUSIÓN:** PorEsto! es un medio legítimo y establecido. Mena escribe ahí como columnista invitado, no como operador del medio.

---

### HALLAZGO 8: PROYECTO PUENTE - MEDIO INDEPENDIENTE DE SONORA

- Director General: **Luis Alberto Medina**
- Infraestructura: Amazon AWS (profesional)
- Google Analytics: G-HSP0D2B3FE
- AdSense: ca-pub-2299250803327721
- Facebook Pixel: 3446853778764149
- Equipo completo identificado con emails

**CONCLUSIÓN:** Proyecto Puente es un medio profesional de Sonora (no Yucatán). Es probable que publicó contra Daniela Caballero por nota enviada/filtrada, no por ser parte de la red.

---

## TABLA RESUMEN DE CLUSTERS

| Cluster | Medios | Hosting | Evidencia de conexión |
|---------|--------|---------|----------------------|
| **A - GRILLOS** | Grillo de Yucatán + Grillo Porteño | DigitalOcean | Mismo autor "Grillo Uno", mismo tracker, Jhony Alamilla Castro |
| **A+ - FORMAL** | Formal Prisión | DigitalOcean | Mismo hosting y tracker que Grillos |
| **B - HOSTINGER** | El Principal + Noticias Mérida | Hostinger | Solo hosting compartido |
| **C - INDEPENDIENTES** | PorEsto!, Sol Yucatán | Cloudflare | Medios establecidos, sin conexión técnica |
| **D - EXTERNO** | Proyecto Puente | Amazon AWS | Medio de Sonora, independiente |
| **E - BÁSICO** | El Chismógrafo | Unified Layer | Operación básica, Analytics único |

---

## NOMBRES REALES IDENTIFICADOS

| Medio | Nombre Real | Rol |
|-------|------------|-----|
| Grillo Porteño | **Jhony Alamilla Castro** | Autor/operador |
| Formal Prisión | **Jose Duque** | Autor (¿real o seudónimo?) |
| Noticias Mérida | Gmail genérico | Operador anónimo |
| El Principal | **Rudy Lavalle** (conocido) | Operador |
| PorEsto! | Compañía Editora del Mayab | Empresa |
| Sol Yucatán | Dirección en Chetumal, QR | ¿Operador en Quintana Roo? |
| Proyecto Puente | **Luis Alberto Medina** | Director General |

---

## PRÓXIMOS PASOS INMEDIATOS

1. **Investigar a Jhony Alamilla Castro** - ¿Quién es? ¿Conexión con Vadillo, Mena o Meza?
2. **Investigar a Jose Duque** de Formal Prisión
3. **Verificar el Google Analytics UA-122967539-1** del Chismógrafo en otros sitios
4. **Investigar la conexión Sol Yucatán - Chetumal - Ricardo Ravelo - Proceso**
5. **Buscar el AdSense ca-pub-2882425394935324** de Noticias Mérida en otros sitios


---

## INVESTIGACIÓN: JHONY ALAMILLA CASTRO

### Perfil confirmado:
- **Nombre completo:** Jhony Alamilla Castro
- **Facebook:** @jhonychileseco (5,314 likes)
- **Rol confirmado:** Autor/operador de **El Grillo de Yucatán** Y **Grillo Porteño**
- Firma artículos como: "Por Jhony Alamilla Castro para El Grillo de Yucatán y Notimex"
- También publica en Facebook vía "Notimex" (¿medio propio o colaboración?)
- Escribe columnas de opinión política sobre Yucatán
- Estilo: sarcástico, crítico, provocador

### Conexión familiar INTERESANTE:
- **Jorge Alberto Alamilla Castro** (posible hermano o familiar directo):
  - Esposo de Martha Leticia Núñez Polanco (alcaldesa de Cenotillo, Yucatán)
  - Escándalo en 2018: la alcaldesa le pagó $153,204 pesos de fondos públicos
  - Aparece en Diario Oficial de Yucatán (Feb 2025) en un juicio ejecutivo mercantil como endosatario

### Análisis:
- Jhony Alamilla Castro es el operador REAL de los dos Grillos
- Su familia tiene conexiones políticas locales (PRI/alcaldías)
- La pregunta clave: ¿Quién le paga a Jhony para atacar a Cortés? ¿Vadillo? ¿Mena? ¿Opera de manera independiente?


---

## INVESTIGACIÓN: SOL YUCATÁN / GRUPO SOL CORPORATIVO

**Director General y Fundador:** Pedro Daniel Rodríguez Hernández, nacido en Chetumal, Quintana Roo.

**Grupo Sol Corporativo** es un conglomerado de medios que incluye:
- Sol Yucatán (solyucatan.com / solyucatan.mx)
- Sol Quintana Roo (solquintanaroo.mx)
- Sol de la Mañana (edición impresa en Yucatán, lanzada Nov 2024)
- Agencia de Noticias del Sol (creada Mar 2022)

**Ricardo Ravelo** NO es de Proceso en este contexto. Es **periodista de Grupo Sol Corporativo**, especializado en crimen organizado. Firma como "Ricardo Ravelo/Corresponsalías Nacionales/Grupo Sol Corporativo". Presentó su libro "Fentanilo: La Era Diabólica de las Drogas" bajo el sello de Grupo Sol (Oct 2025).

**Dato interesante:** En Sep 2025, Sol Yucatán reportó que "intentaron tirar su servidor" por publicaciones sobre el gobierno. Esto sugiere que el medio ha tenido conflictos con actores políticos.

**Conclusión:** Sol Yucatán es un medio independiente con base en Quintana Roo que se expandió a Yucatán. Pedro Daniel Rodríguez Hernández es su dueño real. No parece ser parte de la red de Vadillo o Mena, sino un medio que publica notas que le llegan (posiblemente filtradas por Rosado Pat u otros).

---

## INVESTIGACIÓN: JOSE DUQUE (FORMAL PRISIÓN)

No se encontró información específica sobre "Jose Duque" como periodista en Yucatán. El nombre podría ser un seudónimo. Formal Prisión se autodescribe como "Revista policiaca" y opera desde Mérida. Su página de Facebook tiene actividad regular pero no revela al operador real. El hecho de que comparta hosting (DigitalOcean) con los Grillos es la conexión más fuerte.
