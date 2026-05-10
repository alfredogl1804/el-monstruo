# Runbook: Rotación de BITWARDEN_MASTER_PASSWORD

**Credencial**: Bitwarden master password (no es API token, es contraseña humana)
**Ubicación primaria**: memoria de Alfredo + posible registro físico en bóveda offline
**Frecuencia objetivo**: 90 días (riesgo crítico: llave maestra de bóveda con 8+ items)
**Riesgo si comprometida**: Catastrófico (acceso a 8 items incluyendo Supabase login, GitHub PATs, Stripe, HubSpot, MCP wrappers)
**Tiempo estimado de rotación**: 20 minutos
**Responsable**: Alfredo (no delegable, requiere interacción humana)
**Sprint origen**: S-003.A (post-incidente exposure 2026-05-10)
**Referencias**: DSC-S-001, DSC-S-008

---

## Cuándo rotar

La rotación es obligatoria cuando ocurre cualquiera de las siguientes condiciones: la master password cumple 90 días desde su última rotación, hay sospecha de exposición (compartida en chat con AI, escrita en post-it visible, dictada en llamada con grabación, ingresada en dispositivo no propio), un dispositivo con sesión de Bitwarden activa se pierde o roba, o un colaborador con acceso a la bóveda compartida deja el proyecto.

**Trigger inmediato actual**: la master password fue compartida en chat con Manus el 2026-05-10 durante el sprint S-002.5. Este runbook se ejecuta como remediación pendiente desde esa fecha.

## Pre-requisitos

Acceso al dispositivo principal donde Bitwarden está instalado (web app, app desktop, o app móvil). Sesión actual de Bitwarden activa o capacidad de iniciar sesión con la master password vigente. Conocimiento del recovery key (Bitwarden no permite recuperar password si se pierde, sólo recovery key permite acceso de emergencia). Acceso a un generador de passwords seguro o capacidad de generar passphrase memorable de 5+ palabras aleatorias (método diceware).

## Pasos de ejecución

### Paso 1 — Verificar y respaldar el recovery key

Antes de cambiar la master password, confirmar que el recovery key está documentado de forma offline y accesible. Si no se encuentra, generar uno nuevo desde Settings → Account → Recovery key, y guardar físicamente en bóveda offline o caja fuerte. **Esta verificación es no-negociable**: una rotación de master password sin recovery key implica riesgo de pérdida total de acceso si la nueva password se olvida.

### Paso 2 — Generar la nueva master password

Opciones recomendadas, en orden de preferencia:

1. **Diceware passphrase** (recomendado): generar 5-7 palabras aleatorias del diccionario diceware (https://www.eff.org/dice). Ejemplo de formato: `correct-horse-battery-staple-azul-tigre-roma`. Memorable, alta entropía (>80 bits), resistente a ataques de diccionario.

2. **Password generado**: usar Bitwarden's password generator o `pwgen -s 24 1` para 24 caracteres aleatorios. Difícil de memorizar, requiere sesiones biométricas habilitadas en todos los dispositivos.

3. **Frase semántica con sustituciones**: frase memorable con sustituciones consistentes. Ejemplo: `Mi-N3greta-corre-en-el-Monstruo-2026!`. Menor entropía que diceware pero más memorable.

**Restricciones**: mínimo 16 caracteres. Debe incluir mayúsculas, minúsculas, números y símbolos. **No reusar passwords de otros servicios**. **No incluir información personal trivial** (nombre, fecha nacimiento, mascota).

### Paso 3 — Cambiar la master password en Bitwarden

Login en https://vault.bitwarden.com con la password actual. Settings → Account → Change Master Password. Ingresar:

- Current Master Password: `<password actual>`
- New Master Password: `<password generada en Paso 2>`
- Confirm New Master Password: idem
- (Opcional) Master Password Hint: pista que NO revele la password (ej: "frase de la oración familiar")

Click "Change Master Password". Bitwarden cerrará sesión en todos los dispositivos automáticamente (este es el comportamiento esperado).

### Paso 4 — Re-autenticar en cada dispositivo

Después del cambio, cada dispositivo con Bitwarden instalado mostrará "Session expired". Iniciar sesión en cada uno con la nueva master password:

- Browser extension (Chrome/Safari/Firefox)
- Desktop app
- Mobile app (iOS/Android)
- CLI (`bw login`, después `bw unlock`)

Si tienes 2FA habilitado (recomendado), tendrás que ingresar el código TOTP en cada dispositivo. Habilitar biometría (Face ID, Touch ID) en cada dispositivo después del unlock para evitar tener que ingresar la master password constantemente.

### Paso 5 — Verificar acceso a items críticos

Probar acceso a los 3 items más críticos para confirmar que la rotación no comprometió la bóveda:

1. `supabase` — acceso al login de supabase.com
2. `Monstruo Claude Desktop MCP supabase` — acceso al PAT de Supabase
3. `GitHub PAT - el-monstruo-kernel-2026-05` — acceso al PAT de GitHub

Si algún item es inaccesible o el contenido aparece corrupto, contactar soporte de Bitwarden inmediatamente.

### Paso 6 — Actualizar la sesión activa de Bitwarden CLI en el Mac

```bash
bw logout
bw login alfredogl1.gongora@gmail.com
# Ingresar la nueva master password cuando se solicite
export BW_SESSION=$(bw unlock --raw)
echo "Session OK"
```

Verificar que las integraciones que dependen de Bitwarden CLI siguen funcionando (scripts del Sprint S-002.5 que extraen secrets via `bw get password`).

### Paso 7 — Documentar la rotación

Actualizar `bridge/credentials_inventory.md` línea de `BITWARDEN_MASTER_PASSWORD` con `last_rotated_at: YYYY-MM-DD`. Marcar el incidente del 2026-05-10 como **REMEDIADO** en `discovery_forense/INCIDENTES/`. Agregar entrada al `bridge/rotation_log.md`:

```markdown
## Rotación 2026-XX-XX — BITWARDEN_MASTER_PASSWORD

- Razón: remediación incidente exposure 2026-05-10 (chat con Manus)
- Ejecutado por: Alfredo
- Método: <diceware / generated / phrase>
- Verificación recovery key: <previa al cambio / posterior al cambio>
- Resultado: <todos los items accesibles / items con problemas: ...>
- Tiempo total: <minutos>
- Notas: <relevantes>
```

Commit y push.

## No-rollback policy

A diferencia de credenciales de servicios, una password humana no permite rollback fácil: una vez cambiada, la anterior queda invalidada. Por eso el Paso 1 (recovery key) es crítico. Si Paso 5 detecta items corruptos, NO intentar rollback con la password antigua: contactar soporte de Bitwarden para recovery vía recovery key.

## Errores comunes

Si Bitwarden rechaza la nueva password con "Master password does not meet minimum requirements", revisar las restricciones del Paso 2. Si después del cambio algún dispositivo no permite login, verificar que la nueva password se está escribiendo correctamente (probar en un campo de texto plano primero, no en el campo de password). Si el recovery key no funciona, contactar soporte (https://bitwarden.com/help/contact-support).

## Validación post-rotación

7 días después de la rotación, ejecutar el siguiente comando para confirmar que la sesión de Bitwarden CLI sigue válida y los scripts del Mac que dependen de ella funcionan:

```bash
bw status
bw list items --search supabase | head -3
```

Si alguno falla, re-autenticar y actualizar la documentación de runbooks que dependen de `BW_SESSION`.

---

**Última actualización**: 2026-05-10 (creación del runbook post-incidente, Sprint S-003.A)
