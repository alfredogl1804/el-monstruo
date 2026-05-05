# Checklist iOS Code Signing — Acción humana de Alfredo

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Bloquea:** Sprint Mobile 1.C (Voice Input en Flutter, requiere build a iPhone físico)
> **NO bloquea:** Sprint Mobile 1.A (File Upload, corre en macOS desktop sin certs)
> **Tiempo estimado tuyo:** ~45-60 min (la primera vez, después es trivial)

---

## Por qué necesitamos esto

Sprint Mobile 1.C activa el voice input. Para probarlo necesitamos build de la app Flutter en un iPhone físico (el Simulator no expone el micrófono real correctamente). Para hacer build a device físico, Apple exige firma digital con un Developer Account + provisioning profile.

NO necesitamos publicar a la App Store todavía (post-v1.0). Solo build firmado para tu device.

## Pre-requisitos

- ✅ Apple ID (que ya tenés)
- ✅ Mac con Xcode 15+ instalado
- ⚠️ Apple Developer Program membership ($99 USD/año) — **¿la tenés ya?**
  - Si **NO** la tenés: necesitás registrarte en https://developer.apple.com/programs/ antes de empezar
  - Si **SÍ** la tenés: salteás el paso 1

## Checklist paso a paso

### Paso 1 — Apple Developer Program (saltear si ya tenés)

1. Ir a https://developer.apple.com/programs/
2. Click "Enroll"
3. Login con tu Apple ID
4. Completar enrollment como "Individual" (más simple) o "Organization" (si querés Hive Business Center como entidad)
5. Pagar $99 USD/año con tarjeta
6. Esperar aprobación (de 24h a 48h, a veces inmediato)
7. Confirmar que tu cuenta dice "Apple Developer Program — Active" en https://developer.apple.com/account/

### Paso 2 — Registrar tu device físico

1. En tu iPhone: Settings → General → About → scroll hasta encontrar "Identifier" → guardalo (es un UUID largo)
   - Alternativa: conectá el iPhone a tu Mac, abrí Xcode → Window → Devices and Simulators → seleccioná tu iPhone → copiá "Identifier"
2. Ir a https://developer.apple.com/account/resources/devices/list
3. Click "+" → "Register a Device"
4. Name: "iPhone 17 Pro Alfredo" (o como quieras)
5. Pegá el UUID
6. Continue → Register

### Paso 3 — Crear App ID

1. Ir a https://developer.apple.com/account/resources/identifiers/list
2. Click "+" → "App IDs" → Continue
3. Type: "App"
4. Description: "El Monstruo Mobile"
5. Bundle ID: Explicit → `com.elmonstruo.app` (o el que quieras, pero anotalo, lo necesitás después)
6. Capabilities: marcá las que la app va a usar:
   - ✅ Push Notifications (futuro)
   - ✅ Audio, AirPlay, and Picture in Picture (para voice input)
   - ✅ App Groups (futuro)
7. Continue → Register

### Paso 4 — Crear Provisioning Profile (Development)

1. Ir a https://developer.apple.com/account/resources/profiles/list
2. Click "+" → "iOS App Development" → Continue
3. App ID: seleccioná el que recién creaste (`com.elmonstruo.app`)
4. Certificates: marcá tu certificado de desarrollo (Xcode lo crea automático la primera vez que abrís un proyecto iOS — si no aparece, abrí Xcode y firmá una app de prueba primero)
5. Devices: marcá tu iPhone registrado
6. Provisioning Profile Name: "El Monstruo Dev iPhone Alfredo"
7. Generate → Download
8. Doble-click el archivo `.mobileprovision` descargado para instalarlo

### Paso 5 — Configurar el proyecto Flutter

1. Abrí terminal y andá al repo: `cd ~/el-monstruo`
2. Editá `apps/mobile/ios/Runner.xcodeproj/project.pbxproj` o usá Xcode:
   ```bash
   open apps/mobile/ios/Runner.xcworkspace
   ```
3. En Xcode: seleccioná "Runner" en el sidebar → tab "Signing & Capabilities"
4. Marcá "Automatically manage signing"
5. Team: seleccioná tu Apple Developer Team
6. Bundle Identifier: `com.elmonstruo.app` (mismo del paso 3)
7. Si hay errores en rojo → click "Try Again" o "Fix Issue"
8. Cuando esté verde, cerrá Xcode

### Paso 6 — Verificar que el build firmado funciona

1. Conectá tu iPhone a la Mac con cable
2. En tu iPhone: Settings → General → VPN & Device Management → Trust your developer certificate (la primera vez)
3. En terminal:
   ```bash
   cd ~/el-monstruo/apps/mobile
   flutter devices
   ```
   Deberías ver tu iPhone listado.
4. Build:
   ```bash
   flutter run -d <ID_DE_TU_IPHONE> --release
   ```
   La primera vez tarda ~5-10 min. Las siguientes ~1-2 min.
5. La app debería abrirse en tu iPhone con el ícono y nombre del Monstruo.

### Paso 7 — Confirmar al Cowork

Cuando el build firmado en iPhone funcione, mandame mensaje en el chat:

> **"iOS code signing OK — Sprint Mobile 1.C desbloqueado"**

Yo despacho la task del 1.C al Memento y arrancan voice input con build directo a tu iPhone para testing.

## Si te trabás en algún paso

Avisame con captura de pantalla del error. Los pasos más comunes que fallan:

- **"No certificates found"** → Abrí Xcode → Preferences → Accounts → tu Apple ID → "Manage Certificates" → click "+" → "Apple Development". Después volvé al paso 4.
- **"Bundle ID is not available"** → alguien más ya lo registró. Cambiá a `com.elmonstruo.app.alfredo` o similar.
- **"Could not install on device"** → tocá "Trust This Computer" en el iPhone cuando aparezca el popup.
- **"App could not be verified"** en el iPhone → Settings → General → VPN & Device Management → Trust developer certificate.

## Tiempo total estimado

- Si ya tenés Apple Developer Program: **30-45 min**
- Si necesitás suscribirte primero: **2-3 horas calendario** (esperando aprobación) pero solo **45-60 min de trabajo activo tuyo**

## NO necesitás hacer ahora

- TestFlight setup (post-v1.0)
- App Store Connect listing (post-v1.0)
- Production provisioning profile (post-v1.0)
- Push Notifications certificates (post-v1.0)

Solo el setup mínimo para build firmado a tu device personal.

— Cowork (Hilo B)
