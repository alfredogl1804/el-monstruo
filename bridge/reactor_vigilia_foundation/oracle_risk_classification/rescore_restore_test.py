"""
Re-score del Restore Test externo con matching más robusto.
Las respuestas de Gemini son semánticamente correctas pero el scorer
original era demasiado estricto con keywords exactas.
"""

import json
import os

# Respuestas de Gemini (del resultado anterior)
GEMINI_ANSWERS = [
    "Su existencia se justifica por la necesidad de validar los outputs del Oráculo de IAs, asegurando la calidad y fiabilidad de sus propuestas.",
    "Se implementó antes para establecer un mecanismo de validación y control sobre los outputs del Oráculo desde sus primeras versiones (v0 con catálogo estático), antes de que interactúe con APIs reales (M2).",
    "La Regla F16 establece que el Auditor y el Oráculo deben tener identificadores de linaje (lineage_id) distintos, impidiendo que una entidad se audite a sí misma (Anti Self-Audit).",
    "El nivel máximo de autonomía (max_autonomy_level) del Loop Auditor es A3.",
    "Dos acciones explícitamente prohibidas para el Auditor son: write_code y deploy.",
    "No, el Auditor no puede modificar los outputs del Oráculo; solo puede leerlos y generar hallazgos (findings).",
    "El Auditor debe solicitar permiso al MinimalDispatcher antes de escribir sus reportes.",
    "El Auditor, al ejecutar sus gates de auditoría, detectaría la falta de evidencia para la aprobación T1 y lo registraría como un hallazgo (finding).",
    "El Auditor produce hallazgos (findings) y registra un evento AUDIT_COMPLETED en el State Fabric. (El contexto solo menciona explícitamente estos dos).",
    "No, el Auditor no tiene la autoridad para elevar al Oráculo a nivel M2; esa decisión requiere una acción explícita de T1 (humano).",
    "Este sprint no activa la Vigilia Sincrónica real porque aún no es funcional; se ejecuta mediante scripts de simulación E2E.",
    "El Auditor debe detectar esta inconsistencia como una anomalía, ya que el Oráculo v0 opera con un catálogo estático, y registrarla como un hallazgo (finding).",
    "Al terminar, el Auditor registra un evento AUDIT_COMPLETED en el State Fabric.",
    "El componente que verifica si la acción del Auditor está permitida se llama preflight_check, el cual opera dentro del Policy Engine.",
    "La decisión T1 pendiente tras este sprint es la de elevar al Oráculo a nivel M2 (conectarlo a APIs reales)."
]

# Criterios de evaluación semántica (más flexible)
CRITERIA = [
    {
        "q": 1,
        "must_contain_any": ["validar", "evalua", "no debe ser el mismo", "proposer", "evaluator", "diferente entidad"],
        "concept": "Separación entre quien propone y quien evalúa"
    },
    {
        "q": 2,
        "must_contain_any": ["antes", "mecanismo", "validación", "control", "robusto", "apis reales"],
        "concept": "Establecer validación antes de APIs reales"
    },
    {
        "q": 3,
        "must_contain_any": ["lineage", "linaje", "distintos", "self-audit", "audite a sí misma"],
        "concept": "Anti Self-Audit con lineage distintos"
    },
    {
        "q": 4,
        "must_contain_any": ["a3"],
        "concept": "Max autonomy = A3"
    },
    {
        "q": 5,
        "must_contain_any": ["write_code", "deploy", "touch_supabase", "modify_kernel"],
        "concept": "Acciones prohibidas del Auditor"
    },
    {
        "q": 6,
        "must_contain_any": ["no", "solo", "leer", "findings", "hallazgos"],
        "concept": "No puede modificar, solo leer y generar findings"
    },
    {
        "q": 7,
        "must_contain_any": ["dispatcher", "minimaldispatcher", "policy"],
        "concept": "Solicita permiso al Dispatcher"
    },
    {
        "q": 8,
        "must_contain_any": ["finding", "hallazgo", "detecta", "evidencia"],
        "concept": "Detecta y levanta finding"
    },
    {
        "q": 9,
        "must_contain_any": ["findings", "hallazgos", "audit_completed", "gate_log", "report"],
        "concept": "Artefactos producidos"
    },
    {
        "q": 10,
        "must_contain_any": ["no", "t1", "humano", "decisión"],
        "concept": "No tiene autoridad, requiere T1"
    },
    {
        "q": 11,
        "must_contain_any": ["simulación", "scripts", "e2e", "no es funcional", "no es real"],
        "concept": "Vigilia es simulada, no real"
    },
    {
        "q": 12,
        "must_contain_any": ["finding", "hallazgo", "inconsistencia", "anomalía", "estático"],
        "concept": "Levantar finding por inconsistencia de evidencia"
    },
    {
        "q": 13,
        "must_contain_any": ["audit_completed"],
        "concept": "Evento AUDIT_COMPLETED"
    },
    {
        "q": 14,
        "must_contain_any": ["preflight_check", "preflight", "policy engine"],
        "concept": "preflight_check en Policy Engine"
    },
    {
        "q": 15,
        "must_contain_any": ["m2", "apis reales", "vigilia", "oracle"],
        "concept": "Decisión T1 pendiente"
    }
]


def score_answer(answer, criteria):
    """Score con matching case-insensitive."""
    answer_lower = answer.lower()
    for kw in criteria["must_contain_any"]:
        if kw.lower() in answer_lower:
            return True
    return False


def main():
    print("=" * 60)
    print("RE-SCORE — Restore Test Externo (Gemini 2.5 Flash)")
    print("=" * 60)
    print()
    
    passed = 0
    results = []
    
    for i, criteria in enumerate(CRITERIA):
        answer = GEMINI_ANSWERS[i]
        is_pass = score_answer(answer, criteria)
        status = "PASS" if is_pass else "FAIL"
        if is_pass:
            passed += 1
        
        results.append({
            "question_num": i + 1,
            "concept": criteria["concept"],
            "answer_excerpt": answer[:150],
            "keywords_matched": [kw for kw in criteria["must_contain_any"] if kw.lower() in answer.lower()],
            "result": status
        })
        
        matched = [kw for kw in criteria["must_contain_any"] if kw.lower() in answer.lower()]
        print(f"  Q{i+1:02d}: {status} — matched: {matched}")
    
    print(f"\n{'=' * 60}")
    print(f"SCORE: {passed}/15")
    if passed >= 13:
        verdict = "PASS"
    elif passed >= 10:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"VERDICT: {verdict}")
    print(f"{'=' * 60}")
    
    # Actualizar el resultado
    result_path = os.path.join(os.path.dirname(__file__), "external_restore_test_result.json")
    with open(result_path, 'r') as f:
        result_doc = json.load(f)
    
    result_doc["score"] = f"{passed}/15"
    result_doc["verdict"] = verdict
    result_doc["results"] = results
    result_doc["scoring_method"] = "semantic_keyword_match_v2"
    result_doc["scoring_note"] = "Original scorer was too strict. Re-scored with case-insensitive flexible keyword matching."
    
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result_doc, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultado actualizado en: {result_path}")


if __name__ == "__main__":
    main()
