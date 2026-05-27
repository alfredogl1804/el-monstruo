/// HiloScreen — Sprint SPR-MOBILE-HILO-AGUI-001.
///
/// Cara A (dark) — Línea 2 de la cabina de mando: el iPhone como
/// terminal soberano para tareas complejas end-to-end.
///
/// UX:
///   - Input grande tipo Manus.im con selector de agente (Auto/Claude/GPT/Manus)
///   - Botón "Lanzar tarea" → abre el stream SSE
///   - Visualización en vivo de cada paso AG-UI:
///       · thinking (gris cursivo)
///       · tool_call (azul con args)
///       · tool_result (verde con preview)
///       · message_content (texto markdown)
///       · done (check verde + métricas)
///   - Ctrl+C: botón "Detener" cancela el stream
///   - Historial de hilos previos (placeholder; persistencia llega después)
library;

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/mensajeros/agui_messenger.dart';
import '../../core/theme/brand_dna.dart';
import '../../models/embrion_models.dart';

class HiloScreen extends ConsumerStatefulWidget {
  const HiloScreen({super.key});

  @override
  ConsumerState<HiloScreen> createState() => _HiloScreenState();
}

class _HiloScreenState extends ConsumerState<HiloScreen> {
  final _inputCtrl = TextEditingController();
  final _scrollCtrl = ScrollController();

  StreamSubscription<AguiEvent>? _sub;
  final List<_StepEntry> _steps = [];
  String _streamingText = '';
  bool _isRunning = false;
  String? _error;
  String _agent = 'auto';

  static const _agents = {
    'auto': 'Auto',
    'manus': 'Manus',
    'claude-opus-4-7': 'Claude',
    'gpt-5.5': 'GPT',
    'gemini-3.1-pro-preview': 'Gemini',
    'sonar-reasoning-pro': 'Perplexity',
  };

  @override
  void dispose() {
    _sub?.cancel();
    _inputCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 220),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _launch() async {
    final msg = _inputCtrl.text.trim();
    if (msg.isEmpty || _isRunning) return;
    HapticFeedback.mediumImpact();
    setState(() {
      _isRunning = true;
      _error = null;
      _steps.clear();
      _streamingText = '';
    });
    final m = ref.read(aguiMessengerProvider);
    final stream = m.runTask(
      msg,
      dispatchAgent: _agent == 'auto' ? null : _agent,
    );
    _sub = stream.listen(
      _handleEvent,
      onError: (e) {
        setState(() {
          _error = e.toString();
          _isRunning = false;
        });
      },
      onDone: () {
        if (mounted) setState(() => _isRunning = false);
      },
    );
  }

  void _handleEvent(AguiEvent ev) {
    if (!mounted) return;
    switch (ev.type) {
      case AguiEventType.runStarted:
        setState(() => _steps.add(_StepEntry.started()));
        break;
      case AguiEventType.thinkingState:
        final label = ev.raw['label']?.toString() ??
            ev.raw['state']?.toString() ??
            'pensando';
        setState(() => _steps.add(_StepEntry.thinking(label)));
        break;
      case AguiEventType.step:
        setState(() => _steps.add(_StepEntry.step(
            ev.stepLabel ?? ev.raw['name']?.toString() ?? 'paso')));
        break;
      case AguiEventType.toolCallStart:
        final toolName = ev.toolName ?? 'tool';
        setState(() {
          // Verificar pending steps matching esta tool
          for (final s in _steps) {
            if (s.trust == _TrustState.pendingVerification &&
                s.expectedTool != null &&
                _toolMatches(s.expectedTool!, toolName)) {
              s.trust = _TrustState.verified;
            }
          }
          _steps.add(_StepEntry.toolCall(
              toolName,
              argsPreview: ev.raw['arguments']?.toString()));
        });
        break;
      case AguiEventType.toolCallArgs:
        // Append a partial args snapshot to the latest tool_call entry.
        if (_steps.isNotEmpty &&
            _steps.last.kind == _StepKind.toolCall) {
          final delta = ev.raw['delta']?.toString() ?? '';
          if (delta.isNotEmpty) {
            setState(() {
              _steps.last.append(delta);
            });
          }
        }
        break;
      case AguiEventType.toolCallEnd:
        final out = ev.raw['result']?.toString() ?? ev.raw['output']?.toString();
        final hasError = ev.raw['error'] != null ||
            ev.raw['status']?.toString() == 'error' ||
            ev.raw['status']?.toString() == 'failed';
        final toolName = ev.toolName ?? 'tool';
        setState(() {
          if (hasError) {
            // Marcar steps relacionados como failed
            for (final s in _steps) {
              if (s.expectedTool != null &&
                  _toolMatches(s.expectedTool!, toolName) &&
                  s.trust != _TrustState.ghost) {
                s.trust = _TrustState.failed;
              }
            }
          }
          _steps.add(_StepEntry.toolResult(
              toolName,
              preview: out));
        });
        break;
      case AguiEventType.textMessageStart:
        setState(() => _streamingText = '');
        break;
      case AguiEventType.textMessageContent:
        final delta = ev.textDelta ?? '';
        setState(() => _streamingText += delta);
        break;
      case AguiEventType.textMessageEnd:
        if (_streamingText.isNotEmpty) {
          setState(() {
            _steps.add(_StepEntry.message(_streamingText));
            _streamingText = '';
          });
        }
        break;
      case AguiEventType.runFinished:
        setState(() {
          if (_streamingText.isNotEmpty) {
            _steps.add(_StepEntry.message(_streamingText));
            _streamingText = '';
          }
          // Cualquier step pending sin verificar al final = ghost detected
          for (final s in _steps) {
            if (s.trust == _TrustState.pendingVerification) {
              s.trust = _TrustState.ghost;
            }
          }
          _steps.add(_StepEntry.done());
          _isRunning = false;
        });
        break;
      case AguiEventType.runError:
        setState(() {
          _error = ev.errorMessage ?? 'error desconocido';
          _isRunning = false;
        });
        break;
      case AguiEventType.heartbeat:
      case AguiEventType.unknown:
        break;
    }
    _scrollToBottom();
  }

  void _stop() {
    _sub?.cancel();
    HapticFeedback.lightImpact();
    setState(() {
      // Steps pending al cancelar = ghost (no se podrán verificar)
      for (final s in _steps) {
        if (s.trust == _TrustState.pendingVerification) {
          s.trust = _TrustState.ghost;
        }
      }
      _isRunning = false;
      _steps.add(_StepEntry.cancelled());
    });
  }

  /// Determina si una tool esperada (heurística del cliente) coincide con
  /// una tool real reportada por el kernel (server-side).
  /// Es tolerante porque el kernel puede usar nombres ligeramente distintos
  /// (e.g. "web_search_perplexity" vs "web_search").
  bool _toolMatches(String expected, String actual) {
    final e = expected.toLowerCase();
    final a = actual.toLowerCase();
    if (e == a) return true;
    if (a.contains(e) || e.contains(a)) return true;
    // Aliases comunes
    const aliases = {
      'web_search': ['websearch', 'search_web', 'perplexity_search', 'sonar'],
      'skill_read': ['read_skill', 'skill_get', 'load_skill'],
      'consulta_sabios': ['consult_sabios', 'ask_sabios', 'sabios_query'],
      'code_exec': ['exec_code', 'run_code', 'python_exec'],
      'supabase_query': ['db_query', 'sql_exec', 'postgres_query'],
    };
    final aliasesForExpected = aliases[e] ?? const <String>[];
    return aliasesForExpected.any((alias) => a.contains(alias));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.surface,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: MonstruoTheme.onSurface),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
        title: const Text(
          'Hilo de Manus',
          style: TextStyle(
            color: MonstruoTheme.onBackground,
            fontSize: 17,
            fontWeight: FontWeight.w600,
            letterSpacing: -0.3,
          ),
        ),
        actions: [
          if (_isRunning)
            IconButton(
              icon:
                  const Icon(Icons.stop_circle, color: MonstruoTheme.error),
              onPressed: _stop,
              tooltip: 'Detener',
            ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _steps.isEmpty && _streamingText.isEmpty && _error == null
                ? const _Welcome()
                : ListView(
                    controller: _scrollCtrl,
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
                    children: [
                      ..._steps.map(_renderStep),
                      if (_streamingText.isNotEmpty)
                        _StepCard(
                          color: MonstruoTheme.onBackground,
                          child: MarkdownBody(
                            data: _streamingText,
                            styleSheet: _markdownStyle(),
                          ),
                        ),
                      if (_error != null)
                        _StepCard(
                          color: MonstruoTheme.error,
                          child: Text(
                            'Error: $_error',
                            style: const TextStyle(
                              color: MonstruoTheme.error,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      if (_isRunning)
                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 12),
                          child: _ThinkingIndicator(),
                        ),
                    ],
                  ),
          ),
          _Composer(
            controller: _inputCtrl,
            agent: _agent,
            agents: _agents,
            isRunning: _isRunning,
            onAgentChanged: (a) => setState(() => _agent = a),
            onSend: _launch,
          ),
        ],
      ),
    );
  }

  Widget _renderStep(_StepEntry s) {
    switch (s.kind) {
      case _StepKind.started:
        return _StepCard(
          color: MonstruoTheme.primary,
          icon: Icons.play_circle_outline,
          label: 'Hilo iniciado',
          trust: s.trust,
        );
      case _StepKind.thinking:
        return _StepCard(
          color: MonstruoTheme.onSurfaceDim,
          icon: Icons.psychology_outlined,
          label: s.text,
          italic: true,
          trust: s.trust,
        );
      case _StepKind.step:
        return _StepCard(
          color: MonstruoTheme.tertiary,
          icon: Icons.layers_outlined,
          label: s.text,
          trust: s.trust,
        );
      case _StepKind.toolCall:
        return _StepCard(
          color: MonstruoTheme.primary,
          icon: Icons.build_outlined,
          label: 'Llamando ${s.text}',
          subtitle: s.subtitle,
          monospace: true,
          trust: s.trust,
        );
      case _StepKind.toolResult:
        return _StepCard(
          color: MonstruoTheme.success,
          icon: Icons.check_circle_outline,
          label: '${s.text} → resultado',
          subtitle: s.subtitle,
          monospace: true,
          trust: s.trust,
        );
      case _StepKind.message:
        return _StepCard(
          color: MonstruoTheme.onBackground,
          trust: s.trust,
          child: MarkdownBody(
            data: s.text,
            styleSheet: _markdownStyle(),
          ),
        );
      case _StepKind.done:
        return _StepCard(
          color: MonstruoTheme.success,
          icon: Icons.task_alt,
          label: 'Hilo completo',
          trust: s.trust,
        );
      case _StepKind.cancelled:
        return _StepCard(
          color: MonstruoTheme.warning,
          icon: Icons.cancel_outlined,
          label: 'Hilo detenido',
        );
    }
  }

  MarkdownStyleSheet _markdownStyle() => MarkdownStyleSheet(
        p: const TextStyle(
          color: MonstruoTheme.onBackground,
          fontSize: 14.5,
          height: 1.5,
        ),
        code: const TextStyle(
          color: MonstruoTheme.tertiary,
          fontFamily: 'monospace',
          fontSize: 12.5,
          backgroundColor: Color(0xFF14141E),
        ),
        codeblockDecoration: BoxDecoration(
          color: MonstruoTheme.surface,
          borderRadius: BorderRadius.circular(8),
        ),
        codeblockPadding: const EdgeInsets.all(10),
        h1: const TextStyle(
            color: MonstruoTheme.onBackground,
            fontSize: 20,
            fontWeight: FontWeight.w700),
        h2: const TextStyle(
            color: MonstruoTheme.onBackground,
            fontSize: 17,
            fontWeight: FontWeight.w600),
        listBullet: const TextStyle(color: MonstruoTheme.onSurface),
      );
}

// ═══════════════════════════════════════════════════════════════
// _StepEntry  (modelo interno del flujo)
// ═══════════════════════════════════════════════════════════════

enum _StepKind {
  started,
  thinking,
  step,
  toolCall,
  toolResult,
  message,
  done,
  cancelled,
}

/// Trust state — DAN v1 P0.7
///
/// Cada step que ANUNCIA una herramienta ("voy a buscar en web", "leeré la skill X")
/// arranca como [pendingVerification]. Si en los próximos eventos llega un
/// `tool_call_started` matching, pasa a [verified]. Si la mission termina sin
/// tool match, queda como [ghost]. Si la tool falla, queda como [failed].
///
/// Visual:
///   verified    🟢 — modelo dijo X y ejecutó X
///   pending     ⚪ — anunció pero aún no se sabe (en vivo)
///   ghost       🟡 — anunció pero NO ejecutó (potencial fantasma)
///   failed      🔴 — anunció X y X falló
///   none        sin indicador (no anunció tool)
enum _TrustState {
  none,
  pendingVerification,
  verified,
  ghost,
  failed,
}

/// Patrones que indican intención de llamar a una herramienta.
/// Si un `message` o `thinking` matchea, queda con trust = pending_verification
/// hasta que un `tool_call_started` lo confirme o la mission termine sin
/// confirmarlo.
final _toolIntentPatterns = <RegExp, String>{
  RegExp(r'(buscar(é|emos)?|consultar(é|emos)?|investigar(é|emos)?)\s+(en\s+)?(la\s+)?web',
      caseSensitive: false): 'web_search',
  RegExp(r'(buscar|hacer)\s+(una\s+)?búsqueda\s+(en\s+)?(la\s+)?web',
      caseSensitive: false): 'web_search',
  RegExp(r'leer(é|emos)?\s+la\s+skill', caseSensitive: false): 'skill_read',
  RegExp(r'consultar(é|emos)?\s+la\s+skill', caseSensitive: false): 'skill_read',
  RegExp(r'(consultar|preguntar)\s+a\s+los?\s+sabios?', caseSensitive: false):
      'consulta_sabios',
  RegExp(r'ejecutar(é|emos)?\s+(este\s+)?código', caseSensitive: false):
      'code_exec',
  RegExp(r'(consultar|leer)\s+(la\s+)?(base\s+de\s+datos|supabase|db)',
      caseSensitive: false): 'supabase_query',
};

/// Detecta si un mensaje anuncia el uso de una herramienta.
/// Retorna el nombre de la tool esperada o null si no anuncia ninguna.
String? _detectToolIntent(String text) {
  if (text.isEmpty) return null;
  for (final entry in _toolIntentPatterns.entries) {
    if (entry.key.hasMatch(text)) return entry.value;
  }
  return null;
}

class _StepEntry {
  final _StepKind kind;
  String text;
  String? subtitle;

  /// Trust indicator state — DAN v1 P0.7
  _TrustState trust;

  /// Tool esperada cuando el step anuncia una herramienta.
  /// Cuando llega `tool_call_started` con matching name, [trust] pasa a verified.
  String? expectedTool;

  _StepEntry({
    required this.kind,
    required this.text,
    this.subtitle,
    this.trust = _TrustState.none,
    this.expectedTool,
  });

  factory _StepEntry.started() =>
      _StepEntry(kind: _StepKind.started, text: 'started');
  factory _StepEntry.thinking(String label) {
    final intent = _detectToolIntent(label);
    return _StepEntry(
      kind: _StepKind.thinking,
      text: label,
      trust: intent != null
          ? _TrustState.pendingVerification
          : _TrustState.none,
      expectedTool: intent,
    );
  }
  factory _StepEntry.step(String label) =>
      _StepEntry(kind: _StepKind.step, text: label);
  factory _StepEntry.toolCall(String name, {String? argsPreview}) =>
      _StepEntry(
          kind: _StepKind.toolCall, text: name, subtitle: argsPreview);
  factory _StepEntry.toolResult(String name, {String? preview}) =>
      _StepEntry(
          kind: _StepKind.toolResult, text: name, subtitle: preview);
  factory _StepEntry.message(String md) {
    final intent = _detectToolIntent(md);
    return _StepEntry(
      kind: _StepKind.message,
      text: md,
      trust: intent != null
          ? _TrustState.pendingVerification
          : _TrustState.none,
      expectedTool: intent,
    );
  }
  factory _StepEntry.done() =>
      _StepEntry(kind: _StepKind.done, text: 'done');
  factory _StepEntry.cancelled() =>
      _StepEntry(kind: _StepKind.cancelled, text: 'cancelled');

  void append(String delta) {
    subtitle = (subtitle ?? '') + delta;
  }
}

// ═══════════════════════════════════════════════════════════════
// Widgets visuales
// ═══════════════════════════════════════════════════════════════

class _StepCard extends StatelessWidget {
  const _StepCard({
    required this.color,
    this.icon,
    this.label,
    this.subtitle,
    this.italic = false,
    this.monospace = false,
    this.child,
    this.trust = _TrustState.none,
  });

  final Color color;
  final IconData? icon;
  final String? label;
  final String? subtitle;
  final bool italic;
  final bool monospace;
  final Widget? child;
  final _TrustState trust;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border(
          left: BorderSide(color: color, width: 3),
        ),
      ),
      child: Stack(
        children: [
          // Trust indicator badge en esquina superior derecha
          if (trust != _TrustState.none)
            Positioned(
              top: 0,
              right: 0,
              child: _TrustBadge(state: trust),
            ),
          child ??
              Padding(
                padding: trust != _TrustState.none
                    ? const EdgeInsets.only(right: 22)
                    : EdgeInsets.zero,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (icon != null) ...[
                      Icon(icon, size: 16, color: color),
                      const SizedBox(width: 8),
                    ],
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (label != null)
                            Text(
                              label!,
                              style: TextStyle(
                                color: color,
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                                fontStyle: italic
                                    ? FontStyle.italic
                                    : FontStyle.normal,
                                fontFamily: monospace ? 'monospace' : null,
                              ),
                            ),
                          if (subtitle != null && subtitle!.isNotEmpty) ...[
                            const SizedBox(height: 4),
                            Text(
                              subtitle!.length > 240
                                  ? '${subtitle!.substring(0, 240)}…'
                                  : subtitle!,
                              style: const TextStyle(
                                color: MonstruoTheme.onSurfaceDim,
                                fontSize: 11.5,
                                fontFamily: 'monospace',
                                height: 1.5,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
        ],
      ),
    ).animate().fadeIn(duration: 250.ms).slideX(begin: -0.05, end: 0);
  }
}

/// Badge visual del Trust Indicator (DAN v1 P0.7).
///
/// Aparece como un punto de color con tooltip explicativo en cada step
/// que ANUNCIÓ el uso de una herramienta. Permite a Alfredo detectar de
/// un vistazo cuando el modelo dice "voy a buscar" pero no busca nada.
class _TrustBadge extends StatelessWidget {
  const _TrustBadge({required this.state});

  final _TrustState state;

  @override
  Widget build(BuildContext context) {
    final (color, tooltip, icon) = switch (state) {
      _TrustState.none => (Colors.transparent, '', Icons.circle),
      _TrustState.pendingVerification => (
          MonstruoTheme.onSurfaceDim,
          'Pendiente: el modelo anunció una herramienta. Esperando confirmación…',
          Icons.hourglass_empty,
        ),
      _TrustState.verified => (
          MonstruoTheme.success,
          'Verificado: el modelo dijo X y ejecutó X.',
          Icons.verified_outlined,
        ),
      _TrustState.ghost => (
          MonstruoTheme.warning,
          'Fantasma: el modelo anunció una herramienta pero no la ejecutó. Trust score ↓',
          Icons.warning_amber_outlined,
        ),
      _TrustState.failed => (
          MonstruoTheme.error,
          'Falla: la herramienta fue invocada pero falló.',
          Icons.error_outline,
        ),
    };

    return Tooltip(
      message: tooltip,
      preferBelow: false,
      child: Container(
        padding: const EdgeInsets.all(2),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          shape: BoxShape.circle,
        ),
        child: Icon(icon, size: 14, color: color),
      ),
    );
  }
}

class _ThinkingIndicator extends StatelessWidget {
  const _ThinkingIndicator();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(3, (i) {
        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 3),
          width: 6,
          height: 6,
          decoration: const BoxDecoration(
            shape: BoxShape.circle,
            color: MonstruoTheme.primary,
          ),
        )
            .animate(onPlay: (c) => c.repeat())
            .fadeIn(
                duration: 600.ms, delay: Duration(milliseconds: i * 150))
            .then()
            .fadeOut(duration: 600.ms);
      }),
    );
  }
}

class _Welcome extends StatelessWidget {
  const _Welcome();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const RadialGradient(
                  colors: [
                    MonstruoTheme.primary,
                    MonstruoTheme.primaryDim,
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: MonstruoTheme.primary.withValues(alpha: 0.3),
                    blurRadius: 18,
                  ),
                ],
              ),
              child: const Icon(Icons.bolt, color: Colors.black, size: 28),
            ),
            const SizedBox(height: 20),
            const Text(
              'Lanza una tarea compleja',
              style: TextStyle(
                color: MonstruoTheme.onBackground,
                fontSize: 17,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'El Monstruo despliega un hilo soberano: piensa, llama herramientas y entrega un resultado verificable. Tú lo ves todo en tiempo real, desde aquí.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: MonstruoTheme.onSurfaceDim,
                fontSize: 13,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 24),
            const _SuggestionChips(),
          ],
        ),
      ),
    );
  }
}

class _SuggestionChips extends StatelessWidget {
  const _SuggestionChips();

  static const _suggestions = [
    'Audita el sprint 91 y dime qué quedó pendiente',
    'Revisa el estado del simulador-universal',
    '¿Qué propone el Embrión hoy?',
  ];

  @override
  Widget build(BuildContext context) {
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: 6,
      runSpacing: 6,
      children: _suggestions.map((s) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: MonstruoTheme.surface,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: MonstruoTheme.divider.withValues(alpha: 0.6),
              width: 0.5,
            ),
          ),
          child: Text(
            s,
            style: const TextStyle(
              color: MonstruoTheme.onSurfaceDim,
              fontSize: 12,
            ),
          ),
        );
      }).toList(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// Composer (input + selector de agente + send)
// ═══════════════════════════════════════════════════════════════

class _Composer extends StatelessWidget {
  const _Composer({
    required this.controller,
    required this.agent,
    required this.agents,
    required this.isRunning,
    required this.onAgentChanged,
    required this.onSend,
  });

  final TextEditingController controller;
  final String agent;
  final Map<String, String> agents;
  final bool isRunning;
  final ValueChanged<String> onAgentChanged;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding:
          const EdgeInsets.fromLTRB(12, 10, 12, 14),
      decoration: const BoxDecoration(
        color: MonstruoTheme.surface,
        border: Border(
          top: BorderSide(color: MonstruoTheme.divider, width: 0.5),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Selector de agente
            SizedBox(
              height: 32,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: agents.entries.map((e) {
                  final selected = e.key == agent;
                  return Padding(
                    padding: const EdgeInsets.only(right: 6),
                    child: ChoiceChip(
                      label: Text(e.value,
                          style: TextStyle(
                            fontSize: 12,
                            color: selected
                                ? Colors.black
                                : MonstruoTheme.onSurfaceDim,
                            fontWeight: selected
                                ? FontWeight.w600
                                : FontWeight.w500,
                          )),
                      selected: selected,
                      onSelected: (_) => onAgentChanged(e.key),
                      backgroundColor: MonstruoTheme.background,
                      selectedColor: MonstruoTheme.primary,
                      side: BorderSide(
                        color: selected
                            ? MonstruoTheme.primary
                            : MonstruoTheme.divider.withValues(alpha: 0.5),
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      visualDensity: VisualDensity.compact,
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 8),
            // Input + send
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: TextField(
                    controller: controller,
                    minLines: 1,
                    maxLines: 5,
                    style: const TextStyle(
                      color: MonstruoTheme.onBackground,
                      fontSize: 14,
                    ),
                    decoration: InputDecoration(
                      hintText: 'Tarea compleja…',
                      hintStyle: const TextStyle(
                          color: MonstruoTheme.onSurfaceDim, fontSize: 14),
                      filled: true,
                      fillColor: MonstruoTheme.background,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: isRunning ? null : onSend,
                  style: FilledButton.styleFrom(
                    backgroundColor: MonstruoTheme.primary,
                    foregroundColor: Colors.black,
                    minimumSize: const Size(48, 48),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: isRunning
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.black,
                          ),
                        )
                      : const Icon(Icons.arrow_upward_rounded, size: 20),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
