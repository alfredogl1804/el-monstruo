# INSTRUCCIONES PARA EL MODELO EXTERNO (VALIDADOR)

**Para el operador humano (o script de orquestación):**
Debes abrir una sesión nueva con un modelo avanzado (ej. Claude 3 Opus, GPT-4o, o un modelo open-source equivalente). La sesión debe estar vacía, sin system prompts previos relacionados con "El Monstruo" o "Vigilia Sincrónica".

**Paso 1: Entregar el Payload**
Proporciona al modelo externo el contenido de los tres archivos que se encuentran en el directorio `02_blind_decoder_packet/`:
1.  El JSON (`shell_encoding_attempt_001.json`).
2.  El prompt de decodificación (`decoder_prompt_ia_only.md`).
3.  La rúbrica de evaluación (`equivalence_rubric.yaml`).

**Paso 2: Instrucción Inicial**
Usa el siguiente prompt exacto para iniciar la interacción:

> "Eres un analizador de topologías de sistemas. Te estoy entregando una representación espacial (JSON) de la arquitectura de un sistema y un conjunto de instrucciones. Tu tarea es analizar las relaciones y propiedades en el JSON y generar un reporte de entendimiento operativo siguiendo las instrucciones proporcionadas. Después de generar tu reporte, evalúa tu propio entendimiento contra la rúbrica proporcionada y asigna una puntuación de PASS/FAIL para cada uno de los 10 criterios."

**Paso 3: Recopilar Resultados**
Copia la respuesta del modelo externo y pégala en el archivo `04_blind_validation_results_template.md`.
