#!/usr/bin/env python3
"""Validacion schema.py post-Sprint 88.3 - VISION_GENERATIVA + AGENTES extendido."""
import sys
import importlib.util
from pathlib import Path

# Load schema.py directly, bypassing kernel.catastro.__init__ (which imports httpx)
spec = importlib.util.spec_from_file_location(
    'catastro_schema',
    Path(__file__).parent.parent / 'kernel' / 'catastro' / 'schema.py'
)
schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema)

CatastroVisionGenerativa = schema.CatastroVisionGenerativa
SubdominioVisionGenerativa = schema.SubdominioVisionGenerativa
LicensingRisk = schema.LicensingRisk
DominioAgentes = schema.DominioAgentes
CatastroAgente = schema.CatastroAgente
Macroarea = schema.Macroarea

# Pydantic v2: resolver forward refs en modulo aislado
CatastroVisionGenerativa.model_rebuild(_types_namespace=schema.__dict__)
CatastroAgente.model_rebuild(_types_namespace=schema.__dict__)

print('Imports OK')
print(f'  Subdominios VISION_GENERATIVA: {len(list(SubdominioVisionGenerativa))}')
print(f'  Dominios AGENTES: {len(list(DominioAgentes))}')

# Test 1: Veo 3.1
veo = CatastroVisionGenerativa(
    id='veo_3_1',
    nombre='Veo 3.1',
    proveedor='Google DeepMind',
    subdominio_primario=SubdominioVisionGenerativa.VIDEO_CLIP_GENERATIVO,
    subdominios_secundarios=[SubdominioVisionGenerativa.VIDEO_NARRATIVO_CINEMATICO],
    duracion_max_clip_sec=60,
    audio_nativo=True,
    bonus_curador=15,
    bonus_curador_razon='Trono video_clip_generativo Sprint 88.3',
    licensing_risk=LicensingRisk.LOW,
)
print(f'Test 1 Veo 3.1: subdominio={veo.subdominio_primario.value} bonus={veo.bonus_curador} audio_nativo={veo.audio_nativo}')

# Test 2: rechazar primario en secundarios
try:
    bad = CatastroVisionGenerativa(
        id='bad_test',
        nombre='Bad',
        proveedor='Test',
        subdominio_primario=SubdominioVisionGenerativa.VIDEO_CLIP_GENERATIVO,
        subdominios_secundarios=[SubdominioVisionGenerativa.VIDEO_CLIP_GENERATIVO],
    )
    print('FAIL: deberia rechazar')
    sys.exit(1)
except Exception as e:
    print(f'Test 2 rechaza primario en secundarios: {str(e).splitlines()[0]}')

# Test 3: Manus en agentes_generalistas_autonomos
manus = CatastroAgente(
    id='manus',
    nombre='Manus',
    proveedor='Manus AI',
    dominio=DominioAgentes.AGENTES_GENERALISTAS_AUTONOMOS,
    bonus_curador=10,
    bonus_curador_razon='Trono natural Sprint 88.2',
)
print(f'Test 3 Manus: dominio={manus.dominio.value} bonus={manus.bonus_curador}')

# Test 4: rechazar bonus > 50
try:
    bad = CatastroAgente(
        id='bad',
        nombre='Bad',
        proveedor='Test',
        dominio=DominioAgentes.AGENTES_DESARROLLO,
        bonus_curador=51,
    )
    print('FAIL: deberia rechazar bonus > 50')
    sys.exit(1)
except Exception:
    print('Test 4 rechaza bonus > 50')

# Test 5: Suno con licensing_risk=high
suno = CatastroVisionGenerativa(
    id='suno_v5_5',
    nombre='Suno v5.5',
    proveedor='Suno',
    subdominio_primario=SubdominioVisionGenerativa.MUSICA_GENERADA,
    licensing_risk=LicensingRisk.HIGH,
    consent_required=True,
)
print(f'Test 5 Suno: licensing_risk={suno.licensing_risk.value}')

# Test 6: invariante swarm-multistep
try:
    bad = CatastroAgente(
        id='bad-swarm',
        nombre='Bad',
        proveedor='Test',
        dominio=DominioAgentes.AGENTES_MULTI_SWARM,
        multi_swarm_capable=True,
        multi_step_capable=False,
    )
    print('FAIL: deberia rechazar swarm sin multistep')
    sys.exit(1)
except Exception:
    print('Test 6 invariante swarm-multistep funciona')

print('TODOS LOS TESTS PASARON - schema.py Sprint 88.3 validado')
