# PRÓXIMAS PREGUNTAS DE INVESTIGACIÓN (R0)

Asumiendo que los test de validación ciega y mutación sean exitosos, las siguientes preguntas deben guiar la próxima iteración (v1) del canal SHELL:

1.  **Formatos Binarios:** ¿Cuál es la ganancia real en compresión si pasamos del JSON actual a un formato binario como MessagePack o Protobuf?
2.  **Diccionario Estático:** ¿Cómo se gestiona y sincroniza un diccionario estático de "átomos semánticos" entre diferentes hilos o modelos sin requerir que viajen en cada payload?
3.  **Límites Topológicos:** ¿Cuántas "partículas" y "relaciones" puede procesar una IA antes de que el modelo espacial se vuelva incomprensible? ¿Existe un límite de complejidad topológica?
4.  **Codificación de Restricciones:** ¿Es factible utilizar bitmasks para codificar restricciones operativas (ej. `NO_RUNTIME`, `NO_APP_VISION`) en un solo entero?
5.  **Pérdida de Resolución:** Al eliminar los `semantic_hints`, ¿cuánta resolución operativa se pierde? ¿Puede la topología por sí sola sostener el significado completo?
