/// A2UI renderer — re-export del A2UIRenderer canonizado.
///
/// El path canónico del spec MOBILE-REALIGNMENT-001 (`core/a2ui/renderer.dart`)
/// re-exporta la clase A2UIRenderer (movida y renombrada en T1 desde
/// `features/genui/genui_renderer.dart`). Permite que consumidores externos
/// importen desde el path canónico sin importar el archivo `_renderer.dart`.
///
/// Cuando A2UI v1.0 (PR #92) se mergee, este archivo absorberá el renderer
/// completo + 19 widgets + dispatcher.
///
/// Sprint: MOBILE-REALIGNMENT-001 T2
library;

export 'a2ui_renderer.dart';
