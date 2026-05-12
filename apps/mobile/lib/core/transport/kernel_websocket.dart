/// Kernel WebSocket transport — proxy/re-export para alinear con APP_VISION v1.3.
///
/// El path canonizado por el spec MOBILE-REALIGNMENT-001 (`core/transport/kernel_websocket.dart`)
/// envuelve la API actual de `KernelService` (movido en T1 a `core/mensajeros/kernel_messenger.dart`).
/// Esto preserva 100% del comportamiento existente mientras hace que el path canónico
/// quede disponible para futuros consumidores que prefieran el nombre arquitectónico.
///
/// Sprint: MOBILE-REALIGNMENT-001 T2 (scaffolding `core/` faltante)
/// DSC-G-004: rename evita "service" / "handler" / "utils"; KernelService se mantiene
/// internamente porque renombrar la clase rompería 14+ consumidores y excede scope T2.
library;

export '../mensajeros/kernel_messenger.dart';
