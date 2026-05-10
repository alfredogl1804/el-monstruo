#!/usr/bin/env bash
# Audit no-tokens para archivos del Sprint MEGA-CATASTRO 88.3
set -e
cd "$(dirname "$0")/.."

FILES=(
  "scripts/036_sprint88_1_catalogar_llms_faltantes.sql"
  "scripts/037_sprint88_1_calibrar_empates.sql"
  "scripts/038_sprint88_2_recalibracion_tronos_4_sabios.sql"
  "scripts/039_sprint88_3_documentar_tronos_definitivos.sql"
  "scripts/040_sprint88_3_vision_generativa.sql"
  "scripts/041_sprint88_3_vision_tronos_multidominio.sql"
  "scripts/042_sprint88_3_vision_bonus_topaz.sql"
  "scripts/043_sprint88_3_vision_bonus_veo_final.sql"
  "scripts/044_sprint88_3_vision_bonus_solo_primario.sql"
  "scripts/045_sprint88_3_vision_runway_primario_narrativo.sql"
  "scripts/_apply_migration_039_sprint88_3.py"
  "scripts/_apply_migration_040_sprint88_3.py"
  "scripts/_apply_migration_041_sprint88_3.py"
  "scripts/_generate_migration_040.py"
  "scripts/_inspect_schema_catastro.py"
  "scripts/_verify_estado_pre_039.py"
  "scripts/_test_schema_88_3.py"
  "scripts/_audit_sprint_88_3_files.sh"
  "kernel/catastro/schema.py"
  "discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-007.5_macroarea_vision_generativa_y_tronos_definitivos_agentes.md"
  "bridge/ROADMAP_META_CATASTRO_SPRINT_90.md"
  "bridge/REPORTE_MEGA_CATASTRO_SPRINT_88_3_CIERRE.md"
)

LEAKED=0
for f in "${FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
    LEAKED=$((LEAKED+1))
    continue
  fi
  # Skip self (regex would match itself)
  if [ "$f" = "scripts/_audit_sprint_88_3_files.sh" ]; then
    continue
  fi
  if grep -qE "sb_secret_[A-Za-z0-9]|sbp_[A-Za-z0-9]{20}|service_role|sk-proj-[A-Za-z0-9]" "$f"; then
    echo "LEAK: $f"
    LEAKED=$((LEAKED+1))
  fi
done

if [ $LEAKED -eq 0 ]; then
  echo "AUDIT_OK: ${#FILES[@]} archivos sin secrets ni archivos faltantes"
  exit 0
else
  echo "AUDIT_FAIL: $LEAKED problemas detectados"
  exit 1
fi
