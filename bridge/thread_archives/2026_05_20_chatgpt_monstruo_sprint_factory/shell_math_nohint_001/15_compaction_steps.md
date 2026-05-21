# PASOS DE COMPACTACIÓN (Stage 0 a Stage 1)

Para lograr el "No-Hint Encoding" y mejorar la densidad, se aplican los siguientes pasos de compactación sobre el JSON original:

1.  **Eliminación de Nombres Legibles:**
    *   *Antes:* `"id": "p_unified_face"`
    *   *Después:* `"id": "p_0x02"`
2.  **Eliminación de Claves Descriptivas:**
    *   *Antes:* `"coordinates": { "authority": 8, "risk": 0, "runtime": 1 }`
    *   *Después:* `"C": [8, 0, 1]`
3.  **Tipado Numérico de Relaciones:**
    *   *Antes:* `"type": "synchronizes_with"`
    *   *Después:* `"type": 4`
4.  **Eliminación Total de `semantic_hint`:**
    *   *Antes:* `"semantic_hint": "Este es el nodo central que enruta todo."`
    *   *Después:* (Campo eliminado completamente).
5.  **Minimización de Metadatos:**
    *   *Antes:* `"metadata_tags": ["single_writer_only", "NO_RUNTIME"]`
    *   *Después:* Incorporado en el vector de coordenadas $\mathbf{C}$ o eliminado si es redundante con la topología.

Estos pasos reducen el peso en bytes y tokens, transfiriendo la carga de la "comprensión" desde la lectura de texto hacia la inferencia matemática topológica.
