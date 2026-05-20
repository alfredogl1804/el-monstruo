# Preflight Check - Policy Engine

# Mapeo numérico de los niveles de autonomía para facilitar comparación
AUTONOMY_LEVELS = {
    "A0": 0,
    "A1": 1,
    "A2": 2,
    "A3": 3,
    "A4": 4,
    "A5": 5,
    "A6": 6,
    "A7": 7,
    "A8": 8
}

def check_path_allowed(target_path, allowed_paths):
    if not allowed_paths:
        return True # Si no hay allowlist específico para la acción, se asume permitido (sujeto a otras reglas)
    
    for allowed in allowed_paths:
        if target_path.startswith(allowed):
            return True
    return False

def check_path_forbidden(target_path, forbidden_paths):
    if not forbidden_paths:
        return False
    
    for forbidden in forbidden_paths:
        if target_path.startswith(forbidden):
            return True
    return False

def preflight_check(loop_contract, action_request, registry, state_fabric=None):
    """
    Evalúa si un loop tiene permiso para ejecutar una acción específica.
    Devuelve un tuple (booleano_permitido, string_motivo).
    """
    action_name = action_request.get('action')
    target_path = action_request.get('target_path', '')
    
    # 1. ¿La acción está en el registry?
    if action_name not in registry['actions']:
        return False, f"REJECT: Action '{action_name}' not in registry. Assumed A8 (Blocked)."
    
    action_def = registry['actions'][action_name]
    required_level = action_def.get('autonomy_level_required', 'A8')
    loop_level = loop_contract.get('max_autonomy_level', 'A0')
    
    # 2. ¿Nivel requerido <= Nivel del loop?
    if AUTONOMY_LEVELS.get(required_level, 8) > AUTONOMY_LEVELS.get(loop_level, 0):
        return False, f"REJECT: Autonomy Exceeded. Action requires {required_level}, loop is {loop_level}."
    
    # 3. ¿Requiere firma T1?
    if action_def.get('t1_required', False):
        # En una implementación real, buscaríamos en state_fabric la firma
        t1_approval = action_request.get('t1_approval_present', False)
        if not t1_approval:
            return False, "REJECT: Missing T1 Approval for this action."
            
    # 4. ¿Path prohibido o no permitido?
    # Revisar prohibiciones del loop
    if check_path_forbidden(target_path, loop_contract.get('forbidden_paths', [])):
        return False, f"REJECT: Path '{target_path}' is forbidden by loop contract."
        
    # Revisar restricciones de path de la acción
    if 'allowed_paths' in action_def and target_path:
        if not check_path_allowed(target_path, action_def['allowed_paths']):
            return False, f"REJECT: Path '{target_path}' not in allowed_paths for action '{action_name}'."
            
    # 5. ¿Requiere auditor independiente?
    if action_def.get('auditor_required', False):
        auditor_lineage = action_request.get('auditor_lineage_id')
        loop_lineage = loop_contract.get('lineage_id')
        if not auditor_lineage or auditor_lineage == loop_lineage:
            return False, "REJECT: Auditor Lineage Conflict. Independent auditor required."
            
    # 6. ¿Requiere evidencia?
    if action_def.get('evidence_required', False):
        has_evidence = action_request.get('has_evidence', False)
        if not has_evidence:
            return False, "REJECT: Evidence required but not provided."
            
    return True, "ALLOW"
