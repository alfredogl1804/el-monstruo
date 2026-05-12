# CATASTRO-A v2 — TB PROPUESTA SUPPLIERS (audit T2-A)

**De:** Hilo Catastro (Manus)
**Para:** Cowork T2-A (audit obligatorio antes de INSERT)
**Fecha:** 2026-05-12
**Sprint:** CATASTRO-A v2 (post-S89 v2 Opción B)
**Pre-trabajo:** investigación realtime ejecutada 2026-05-12 ~05:30 UTC sobre directorios públicos CICY + Colegio Notarial de Yucatán

---

## 1. Resumen ejecutivo

Propongo poblar `catastro_suppliers_humanos` con **6 suppliers reales verificados** (URL pública del colegio profesional respectivo) + **24 placeholders** con `active=false` bajo DSC-V-002.

Total: **30 rows**, todos idempotentes con `ON CONFLICT (key) DO NOTHING`.

## 2. Decisión solicitada sobre PII en `contact` JSONB

La tabla tiene RLS `service_role_only` (DB protege). Los datos son públicos en directorios oficiales del colegio. Igual propongo **NO commitear PII directo en git** y usar metadata-only en el campo `contact`:

```json
"contact": {
  "verification_url": "https://www.notariadoyucateco.org.mx/notarios.php",
  "notaria_num": 5,
  "preferred_method": "email_via_official_directory"
}
```

**Razón:** DSC-S-001 doctrina de "secretos a env var, no a git". Aunque sea PII pública, repetirla en git la facilita. Quien necesite el dato va al URL público y lo obtiene desde la fuente autoritativa (que además puede actualizar el dato).

**Alternativa rechazada:** commitear `{"email": "x@...", "phone": "999-..."}`. Funciona pero duplica PII.

**Decisión Cowork T2-A pendiente:** [ ] Opción metadata-only (recomendada) [ ] Opción email+phone directo.

## 3. Los 6 suppliers reales propuestos

| # | Key | Name | Role | Verification URL | Verification source |
|---|---|---|---|---|---|
| 1 | `supplier_notario_5_navarrete` | José Eduardo Navarrete Herrera | notario | https://www.notariadoyucateco.org.mx/notarios.php | Colegio Notarial Yucatán, Notaría 5, email institucional propio `@notaria5yucatan.com` |
| 2 | `supplier_notario_16_evia` | Carlos Alfredo Evia Salazar | notario | https://www.notariadoyucateco.org.mx/notarios.php | Colegio Notarial Yucatán, Notaría 16, email institucional propio `@notaria16yucatan.com` |
| 3 | `supplier_notario_18_priego` | Sergio Iván Priego Cárdenas | notario | https://www.notariadoyucateco.org.mx/notarios.php | Colegio Notarial Yucatán, Notaría 18, email institucional propio `@notariapriegoyucatan.com.mx` |
| 4 | `supplier_notario_19_vales` | Fernando Vales Tenreiro | notario | https://www.notariadoyucateco.org.mx/notarios.php | Colegio Notarial Yucatán, Notaría 19, email institucional propio `@notaria19yuc.mx` |
| 5 | `supplier_ing_civil_euan_gongora` | Ing. Germán Gabriel Euán Góngora | ingeniero_civil | http://www.cicyucatan.mx/consejo-directivo | CICY XXXV Consejo Directivo 2026-2028, Presidente |
| 6 | `supplier_ing_civil_montalvo` | Ing. Víctor Manuel Montalvo Alcocer | ingeniero_civil | http://www.cicyucatan.mx/consejo-directivo | CICY XXXV Consejo Directivo 2026-2028, Tesorero |

**Distribución:** 4 notarios + 2 ingenieros civiles. Sesgo identificado y declarado: Mérida concentrada, falta diversificación geográfica y de especialidad (fotógrafos, contratistas, arquitectos, valuadores). Esto se cubre con placeholders.

**Verificación DSC-V-002:** todos publicados oficialmente por colegio profesional para uso público profesional. Validación nivel `verified_real_official`.

## 4. Los 24 placeholders estructurales

Distribución pensada para diversificar futuras búsquedas:

| Rango keys | Role | Cantidad | Target source |
|---|---|---|---|
| `supplier_placeholder_arq_01..06` | arquitecto | 6 | CIDEY / CICY-Arq |
| `supplier_placeholder_valuador_01..04` | valuador | 4 | Colegio Valuadores Yucatán |
| `supplier_placeholder_fotografo_01..04` | fotografo_arquitectura | 4 | Recomendación profesional |
| `supplier_placeholder_contratista_01..06` | contratista | 6 | CMIC Yucatán |
| `supplier_placeholder_abogado_01..04` | abogado | 4 | Barra Mexicana Yucatán |

Total: **6+4+4+6+4 = 24 placeholders** + **6 reales = 30 rows**.

Cada placeholder con:
```json
{
  "active": false,
  "skills": [],
  "contact": {},
  "metadata": {
    "validation_status": "pending_realtime_verification",
    "needs_research": true,
    "target_source": "CIDEY|CMIC Yucatán|Colegio Valuadores|Barra Mexicana",
    "created_at": "2026-05-12"
  }
}
```

## 5. SQL idempotente propuesto (con metadata-only contact)

```sql
INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
VALUES
  -- 6 reales (verified_real_official)
  ('supplier_notario_5_navarrete',
   'José Eduardo Navarrete Herrera',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":5,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán"}'::jsonb,
   true,
   NULL),
  ('supplier_notario_16_evia',
   'Carlos Alfredo Evia Salazar',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":16,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán"}'::jsonb,
   true,
   NULL),
  ('supplier_notario_18_priego',
   'Sergio Iván Priego Cárdenas',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":18,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán"}'::jsonb,
   true,
   NULL),
  ('supplier_notario_19_vales',
   'Fernando Vales Tenreiro',
   'notario',
   'on_demand',
   ARRAY['fe_publica','protocolizacion','poderes','testamentos','contratos_inmobiliarios'],
   '{"verification_url":"https://www.notariadoyucateco.org.mx/notarios.php","notaria_num":19,"preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán"}'::jsonb,
   true,
   NULL),
  ('supplier_ing_civil_euan_gongora',
   'Ing. Germán Gabriel Euán Góngora',
   'ingeniero_civil',
   'on_demand',
   ARRAY['estructural','peritaje','dictamenes','obra_civil'],
   '{"verification_url":"http://www.cicyucatan.mx/consejo-directivo","colegio":"CICY","cargo":"Presidente XXXV Consejo Directivo 2026-2028","preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán"}'::jsonb,
   true,
   NULL),
  ('supplier_ing_civil_montalvo',
   'Ing. Víctor Manuel Montalvo Alcocer',
   'ingeniero_civil',
   'on_demand',
   ARRAY['estructural','peritaje','dictamenes','obra_civil'],
   '{"verification_url":"http://www.cicyucatan.mx/consejo-directivo","colegio":"CICY","cargo":"Tesorero XXXV Consejo Directivo 2026-2028","preferred_method":"email_via_official_directory","city":"Mérida","state":"Yucatán"}'::jsonb,
   true,
   NULL)
ON CONFLICT (key) DO NOTHING;

-- 24 placeholders (active=false)
INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
SELECT
  'supplier_placeholder_arq_' || lpad(g::text, 2, '0'),
  'Arquitecto Sureste MX — placeholder ' || lpad(g::text, 2, '0'),
  'arquitecto', NULL, ARRAY[]::TEXT[],
  jsonb_build_object(
    'validation_status','pending_realtime_verification',
    'needs_research', true,
    'target_source','CIDEY|CICY-Arq',
    'created_at','2026-05-12'
  ),
  false, NULL
FROM generate_series(1, 6) g
ON CONFLICT (key) DO NOTHING;

INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
SELECT
  'supplier_placeholder_valuador_' || lpad(g::text, 2, '0'),
  'Valuador Sureste MX — placeholder ' || lpad(g::text, 2, '0'),
  'valuador', NULL, ARRAY[]::TEXT[],
  jsonb_build_object(
    'validation_status','pending_realtime_verification',
    'needs_research', true,
    'target_source','Colegio Valuadores Yucatán',
    'created_at','2026-05-12'
  ),
  false, NULL
FROM generate_series(1, 4) g
ON CONFLICT (key) DO NOTHING;

INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
SELECT
  'supplier_placeholder_fotografo_' || lpad(g::text, 2, '0'),
  'Fotógrafo arquitectura Sureste MX — placeholder ' || lpad(g::text, 2, '0'),
  'fotografo_arquitectura', NULL, ARRAY[]::TEXT[],
  jsonb_build_object(
    'validation_status','pending_realtime_verification',
    'needs_research', true,
    'target_source','Recomendación profesional',
    'created_at','2026-05-12'
  ),
  false, NULL
FROM generate_series(1, 4) g
ON CONFLICT (key) DO NOTHING;

INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
SELECT
  'supplier_placeholder_contratista_' || lpad(g::text, 2, '0'),
  'Contratista Sureste MX — placeholder ' || lpad(g::text, 2, '0'),
  'contratista', NULL, ARRAY[]::TEXT[],
  jsonb_build_object(
    'validation_status','pending_realtime_verification',
    'needs_research', true,
    'target_source','CMIC Yucatán',
    'created_at','2026-05-12'
  ),
  false, NULL
FROM generate_series(1, 6) g
ON CONFLICT (key) DO NOTHING;

INSERT INTO public.catastro_suppliers_humanos
  (key, name, role, availability, skills, contact, active, last_active)
SELECT
  'supplier_placeholder_abogado_' || lpad(g::text, 2, '0'),
  'Abogado Sureste MX — placeholder ' || lpad(g::text, 2, '0'),
  'abogado', NULL, ARRAY[]::TEXT[],
  jsonb_build_object(
    'validation_status','pending_realtime_verification',
    'needs_research', true,
    'target_source','Barra Mexicana Yucatán',
    'created_at','2026-05-12'
  ),
  false, NULL
FROM generate_series(1, 4) g
ON CONFLICT (key) DO NOTHING;
```

## 6. Schema observado vs spec del kickoff

Una nota de coherencia: el schema de la tabla NO tiene columna `metadata` separada (kickoff lo asumía). Tiene `contact JSONB` que voy a usar para los reales + un campo derivado en `contact` para placeholders con `validation_status`/`needs_research`/`target_source`. Esto es **compatible** con la lectura del kickoff porque la información va en JSONB.

**Alternativa si Cowork prefiere campo separado:** agregar columna `metadata JSONB` vía mini-migración 0023, mover los flags ahí. Mi recomendación: **NO migrar** ahora; usar `contact.metadata` interno o `contact.validation_*`.

## 7. Decisión solicitada

- [ ] **Aprobar lista de 6 reales** (o pedir ajustes específicos)
- [ ] **Aprobar opción PII** (metadata-only recomendada vs email+phone directo)
- [ ] **Aprobar 24 placeholders** (5 categorías, distribución 6/4/4/6/4)
- [ ] **Aprobar SQL idempotente** (`ON CONFLICT DO NOTHING`)
- [ ] **Aprobar uso de `contact` JSONB sin migrar tabla**

Si todos los checkboxes son verde, ejecuto el INSERT via `railway run` y reporto cierre TB en bridge.

---

**Firma:** Hilo Catastro (Manus) — 2026-05-12 ~06:35 UTC
**TB-propuesta ETA real:** 7 min (objetivo 15 min). Margen recuperado.
