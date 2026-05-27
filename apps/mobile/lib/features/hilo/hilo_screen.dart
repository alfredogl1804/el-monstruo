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
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:url_launcher/url_launcher.dart';
import 'package:uuid/uuid.dart';

import '../../core/mensajeros/agui_messenger.dart';
import '../../core/theme/brand_dna.dart';
import '../../models/embrion_models.dart';
import 'hilo_history.dart';
import 'hilo_preferences.dart';

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
  String? _currentHistoryId;
  String _currentPrompt = '';
  DateTime? _currentStartedAt;

  static const _agents = {
    'auto': 'Auto',
    'manus': 'Manus',
    'claude-opus-4-7': 'Claude',
    'gpt-5.5': 'GPT',
    'gemini-3.1-pro-preview': 'Gemini',
    'sonar-reasoning-pro': 'Perplexity',
  };

  @override
  void initState() {
    super.initState();
    // Ítem G — cargar el último agente seleccionado por el usuario.
    HiloPreferences.getLastAgent().then((a) {
      if (mounted && _agents.containsKey(a)) {
        setState(() => _agent = a);
      }
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    _inputCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  /// Ítem A — graba la entrada inicial del hilo en historial local.
  Future<void> _recordHistoryStart(String prompt, String agent) async {
    final id = const Uuid().v4();
    _currentHistoryId = id;
    _currentPrompt = prompt;
    _currentStartedAt = DateTime.now().toUtc();
    await HiloHistory.add(HiloHistoryEntry(
      id: id,
      prompt: prompt,
      agent: agent,
      status: 'running',
      stepsCount: 0,
      createdAt: _currentStartedAt!,
    ));
  }

  /// Ítem A — cierra la entrada actual con status final + steps count.
  Future<void> _recordHistoryFinish(String status, {String? errorMessage}) async {
    final id = _currentHistoryId;
    if (id == null) return;
    await HiloHistory.update(HiloHistoryEntry(
      id: id,
      prompt: _currentPrompt,
      agent: _agent,
      status: status,
      stepsCount: _steps.length,
      createdAt: _currentStartedAt ?? DateTime.now().toUtc(),
      finishedAt: DateTime.now().toUtc(),
      errorMessage: errorMessage,
    ));
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

  /// S5a — aprueba un HITL request enviando "aprobado" al kernel.
  /// Reusa el thread_id actual via runTask con el mensaje de continuación.
  Future<void> _approveHitl(_StepEntry entry) async {
    if (entry.hitlResolved || _isRunning) return;
    HapticFeedback.mediumImpact();
    setState(() {
      entry.hitlResolved = true;
      _steps.add(_StepEntry.hitlApproved(entry.hitlAction ?? 'acción'));
      _isRunning = true;
      _error = null;
      _streamingText = '';
    });
    final m = ref.read(aguiMessengerProvider);
    final stream = m.runTask(
      'aprobado',
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

  /// S5a — rechaza un HITL request enviando "no" al kernel.
  Future<void> _rejectHitl(_StepEntry entry) async {
    if (entry.hitlResolved || _isRunning) return;
    HapticFeedback.lightImpact();
    setState(() {
      entry.hitlResolved = true;
      _steps.add(_StepEntry.hitlRejected(entry.hitlAction ?? 'acción'));
      _isRunning = true;
      _error = null;
      _streamingText = '';
    });
    final m = ref.read(aguiMessengerProvider);
    final stream = m.runTask(
      'rechazado',
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

  /// S5b — abre URL del artifact en navegador externo.
  Future<void> _openArtifact(String url) async {
    HapticFeedback.lightImpact();
    final uri = Uri.tryParse(url);
    if (uri == null) return;
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {
      // Silencioso — si falla, el usuario puede copiar manualmente.
    }
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
    // Ítem A — abrir entrada de historial.
    await _recordHistoryStart(msg, _agent);
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
        // Ítem A — cerrar entrada como error.
        _recordHistoryFinish('error', errorMessage: e.toString());
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
        // S5a — detectar HITL_REQUIRED en el output del tool.
        final hitl = _detectHitl(out, toolName);
        // S5b — detectar URLs accionables en el output.
        final artifacts = _detectArtifacts(out);
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
          if (hitl != null) {
            _steps.add(_StepEntry.hitlRequest(
              action: hitl.action,
              payload: hitl.payload,
              message: hitl.message,
            ));
          }
          for (final art in artifacts) {
            _steps.add(_StepEntry.artifact(
              url: art.url,
              label: art.label,
              kind: art.kind,
            ));
          }
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
        // Ítem A — cerrar entrada de historial como completed.
        _recordHistoryFinish('completed');
        break;
      case AguiEventType.runError:
        setState(() {
          _error = ev.errorMessage ?? 'error desconocido';
          _isRunning = false;
        });
        // Ítem A — cerrar entrada de historial como error.
        _recordHistoryFinish('error', errorMessage: ev.errorMessage);
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
    // Ítem A — cerrar entrada de historial como cancelled.
    _recordHistoryFinish('cancelled');
  }

  /// Ítem G — persiste la elección de agente cuando el usuario la cambia.
  void _onAgentChanged(String agent) {
    setState(() => _agent = agent);
    HiloPreferences.setLastAgent(agent);
  }

  /// Ítem A — abre el sheet de historial.
  void _openHistory() {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: MonstruoTheme.surface,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => const _HiloHistorySheet(),
    );
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
            )
          else
            IconButton(
              icon: const Icon(
                Icons.history,
                color: MonstruoTheme.onSurfaceDim,
              ),
              onPressed: _openHistory,
              tooltip: 'Historial',
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
            onAgentChanged: _onAgentChanged,
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
      case _StepKind.hitlRequest:
        // S5a — tarjeta interactiva con Aprobar/Rechazar.
        return _HitlRequestCard(
          entry: s,
          onApprove: () => _approveHitl(s),
          onReject: () => _rejectHitl(s),
        );
      case _StepKind.hitlApproved:
        return _StepCard(
          color: MonstruoTheme.success,
          icon: Icons.check_circle,
          label: s.text,
          trust: s.trust,
        );
      case _StepKind.hitlRejected:
        return _StepCard(
          color: MonstruoTheme.warning,
          icon: Icons.do_not_disturb_alt_outlined,
          label: s.text,
          trust: s.trust,
        );
      case _StepKind.artifact:
        // S5b — URL accionable.
        return _ArtifactCard(
          entry: s,
          onOpen: () => _openArtifact(s.artifactUrl ?? ''),
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
  hitlRequest, // S5a — acción HIGH-risk requiere aprobación humana en el iPhone
  hitlApproved, // S5a — marcador de que el usuario aprobó desde la app
  hitlRejected, // S5a — marcador de que el usuario rechazó desde la app
  artifact, // S5b — URL/result accionable (PR, issue, branch, etc.)
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

  /// HITL data — S5a. Solo presente cuando kind == hitlRequest.
  String? hitlAction;
  String? hitlPayload;
  bool hitlResolved;

  /// Artifact data — S5b. Solo presente cuando kind == artifact.
  String? artifactUrl;
  String? artifactKind;

  _StepEntry({
    required this.kind,
    required this.text,
    this.subtitle,
    this.trust = _TrustState.none,
    this.expectedTool,
    this.hitlAction,
    this.hitlPayload,
    this.hitlResolved = false,
    this.artifactUrl,
    this.artifactKind,
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

  /// S5a — HITL approval request card.
  factory _StepEntry.hitlRequest({
    required String action,
    required String payload,
    required String message,
  }) =>
      _StepEntry(
        kind: _StepKind.hitlRequest,
        text: message,
        subtitle: payload,
        hitlAction: action,
        hitlPayload: payload,
      );

  factory _StepEntry.hitlApproved(String action) => _StepEntry(
        kind: _StepKind.hitlApproved,
        text: 'Aprobaste: $action',
      );

  factory _StepEntry.hitlRejected(String action) => _StepEntry(
        kind: _StepKind.hitlRejected,
        text: 'Rechazaste: $action',
      );

  /// S5b — Artifact accionable (URL clickeable).
  factory _StepEntry.artifact({
    required String url,
    required String label,
    required String kind,
  }) =>
      _StepEntry(
        kind: _StepKind.artifact,
        text: label,
        artifactUrl: url,
        artifactKind: kind,
      );

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


// ═══════════════════════════════════════════════════════════════
// _HiloHistorySheet — Ítem A (historial local persistido en Hive)
// ═══════════════════════════════════════════════════════════════

class _HiloHistorySheet extends StatefulWidget {
  const _HiloHistorySheet();

  @override
  State<_HiloHistorySheet> createState() => _HiloHistorySheetState();
}

class _HiloHistorySheetState extends State<_HiloHistorySheet> {
  late List<HiloHistoryEntry> _entries;

  @override
  void initState() {
    super.initState();
    _entries = HiloHistory.list();
  }

  Future<void> _confirmClear() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: MonstruoTheme.surface,
        title: const Text(
          'Borrar historial',
          style: TextStyle(color: MonstruoTheme.onBackground),
        ),
        content: const Text(
          'Esto borra todos los hilos guardados en este iPhone. La acción no se puede deshacer.',
          style: TextStyle(color: MonstruoTheme.onSurfaceDim),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            style: TextButton.styleFrom(foregroundColor: MonstruoTheme.error),
            child: const Text('Borrar'),
          ),
        ],
      ),
    );
    if (ok == true) {
      await HiloHistory.clear();
      if (mounted) {
        setState(() => _entries = []);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      expand: false,
      builder: (_, scrollCtrl) {
        return Column(
          children: [
            // Handle visual
            Container(
              margin: const EdgeInsets.symmetric(vertical: 10),
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: MonstruoTheme.divider,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 4, 12, 8),
              child: Row(
                children: [
                  const Text(
                    'Historial del Hilo',
                    style: TextStyle(
                      color: MonstruoTheme.onBackground,
                      fontSize: 17,
                      fontWeight: FontWeight.w600,
                      letterSpacing: -0.3,
                    ),
                  ),
                  const Spacer(),
                  if (_entries.isNotEmpty)
                    TextButton(
                      onPressed: _confirmClear,
                      style: TextButton.styleFrom(
                        foregroundColor: MonstruoTheme.onSurfaceDim,
                      ),
                      child: const Text('Borrar todo'),
                    ),
                ],
              ),
            ),
            const Divider(color: MonstruoTheme.divider, height: 1),
            Expanded(
              child: _entries.isEmpty
                  ? const _HistoryEmptyState()
                  : ListView.separated(
                      controller: scrollCtrl,
                      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
                      itemCount: _entries.length,
                      separatorBuilder: (_, __) =>
                          const SizedBox(height: 8),
                      itemBuilder: (_, i) =>
                          _HistoryEntryCard(entry: _entries[i]),
                    ),
            ),
          ],
        );
      },
    );
  }
}

class _HistoryEmptyState extends StatelessWidget {
  const _HistoryEmptyState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: const [
            Icon(
              Icons.history_toggle_off,
              color: MonstruoTheme.onSurfaceDim,
              size: 36,
            ),
            SizedBox(height: 12),
            Text(
              'Sin hilos guardados',
              style: TextStyle(
                color: MonstruoTheme.onBackground,
                fontSize: 15,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 4),
            Text(
              'Los hilos que lances desde el iPhone quedan registrados aquí.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: MonstruoTheme.onSurfaceDim,
                fontSize: 12.5,
                height: 1.45,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HistoryEntryCard extends StatelessWidget {
  const _HistoryEntryCard({required this.entry});
  final HiloHistoryEntry entry;

  (Color, IconData, String) get _statusVisual {
    switch (entry.status) {
      case 'completed':
        return (MonstruoTheme.success, Icons.check_circle_outline, 'Completado');
      case 'running':
        return (MonstruoTheme.primary, Icons.bolt, 'En curso');
      case 'cancelled':
        return (MonstruoTheme.warning, Icons.cancel_outlined, 'Detenido');
      case 'error':
        return (MonstruoTheme.error, Icons.error_outline, 'Error');
      default:
        return (MonstruoTheme.onSurfaceDim, Icons.help_outline, entry.status);
    }
  }

  String _formatRelative(DateTime dt) {
    final now = DateTime.now().toUtc();
    final diff = now.difference(dt.toUtc());
    if (diff.inMinutes < 1) return 'hace unos segundos';
    if (diff.inMinutes < 60) return 'hace ${diff.inMinutes} min';
    if (diff.inHours < 24) return 'hace ${diff.inHours} h';
    if (diff.inDays < 7) return 'hace ${diff.inDays} d';
    return '${dt.toLocal().day}/${dt.toLocal().month}/${dt.toLocal().year}';
  }

  @override
  Widget build(BuildContext context) {
    final (color, icon, statusLabel) = _statusVisual;
    return Container(
      decoration: BoxDecoration(
        color: MonstruoTheme.background,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: MonstruoTheme.divider.withValues(alpha: 0.6),
          width: 0.5,
        ),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 14, color: color),
              const SizedBox(width: 6),
              Text(
                statusLabel,
                style: TextStyle(
                  color: color,
                  fontSize: 11.5,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.3,
                ),
              ),
              const Spacer(),
              Text(
                _formatRelative(entry.createdAt),
                style: const TextStyle(
                  color: MonstruoTheme.onSurfaceDim,
                  fontSize: 11,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            entry.displayLabel,
            style: const TextStyle(
              color: MonstruoTheme.onBackground,
              fontSize: 13.5,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: MonstruoTheme.surface,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  entry.agent,
                  style: const TextStyle(
                    color: MonstruoTheme.onSurfaceDim,
                    fontSize: 10.5,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '${entry.stepsCount} steps',
                style: const TextStyle(
                  color: MonstruoTheme.onSurfaceDim,
                  fontSize: 11,
                ),
              ),
              if (entry.errorMessage != null) ...[
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    entry.errorMessage!,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: MonstruoTheme.error,
                      fontSize: 11,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}


// ═══════════════════════════════════════════════════════════════
// S5a — HITL detection + interactive card
// ═══════════════════════════════════════════════════════════════

/// Datos extraídos del output de un tool cuando éste pide aprobación humana
/// antes de ejecutar una acción HIGH-risk (commit, push, payment, etc.).
class _HitlInfo {
  const _HitlInfo({
    required this.action,
    required this.payload,
    required this.message,
  });

  /// Acción canónica que requiere aprobación (ej. "git_push", "payment").
  final String action;

  /// Payload serializado de la acción (JSON o string corto para mostrar).
  final String payload;

  /// Mensaje legible que el usuario verá en la tarjeta de aprobación.
  final String message;
}

/// Detecta si el output de un tool contiene una solicitud HITL.
///
/// Convención esperada del kernel:
///   - JSON con `{"hitl_required": true, "action": "...", "payload": {...}, "message": "..."}`
///   - O un texto plano que contenga `HITL_REQUIRED:` seguido de los campos
///   - O `requires_approval: true` con campos hermanos
///
/// Si no detecta nada, retorna null.
_HitlInfo? _detectHitl(String? out, String toolName) {
  if (out == null || out.isEmpty) return null;
  final trimmed = out.trim();

  // Camino 1 — JSON estructurado.
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    try {
      final decoded = jsonDecode(trimmed);
      if (decoded is Map<String, dynamic>) {
        // Compatibilidad con el kernel real (tools/github.py): cuando una
        // acción de escritura se bloquea por falta de aprobación, el tool
        // devuelve {"error": "HITL_REQUIRED", "action": ..., "message": ...}.
        final errorIsHitl =
            decoded['error']?.toString().toUpperCase() == 'HITL_REQUIRED';
        final flag = decoded['hitl_required'] == true ||
            decoded['requires_approval'] == true ||
            decoded['needs_human'] == true ||
            errorIsHitl;
        if (flag) {
          final action =
              decoded['action']?.toString() ?? toolName;
          final rawPayload = decoded['payload'];
          final payload = rawPayload == null
              ? ''
              : (rawPayload is String
                  ? rawPayload
                  : jsonEncode(rawPayload));
          final message = decoded['message']?.toString() ??
              decoded['reason']?.toString() ??
              'El tool "$toolName" solicita tu aprobación antes de continuar.';
          return _HitlInfo(
            action: action,
            payload: payload,
            message: message,
          );
        }
      }
    } catch (_) {
      // No es JSON válido — caemos al camino 2.
    }
  }

  // Camino 2 — marcador en texto plano.
  final marker = RegExp(
    r'HITL_REQUIRED\s*[:\-]\s*(.+)',
    caseSensitive: false,
    dotAll: true,
  );
  final m = marker.firstMatch(trimmed);
  if (m != null) {
    final body = m.group(1)?.trim() ?? '';
    return _HitlInfo(
      action: toolName,
      payload: body,
      message: 'El tool "$toolName" requiere aprobación: $body',
    );
  }

  return null;
}

/// Tarjeta interactiva — muestra el mensaje HITL y dos botones grandes:
/// Aprobar (verde) y Rechazar (rojo). Un toque ya envía el resultado al kernel.
class _HitlRequestCard extends StatelessWidget {
  const _HitlRequestCard({
    required this.entry,
    required this.onApprove,
    required this.onReject,
  });

  final _StepEntry entry;
  final VoidCallback onApprove;
  final VoidCallback onReject;

  @override
  Widget build(BuildContext context) {
    final resolved = entry.hitlResolved;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: resolved
              ? MonstruoTheme.onSurfaceDim
              : MonstruoTheme.warning,
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.shield_outlined,
                size: 18,
                color: resolved
                    ? MonstruoTheme.onSurfaceDim
                    : MonstruoTheme.warning,
              ),
              const SizedBox(width: 8),
              Text(
                'Aprobación requerida',
                style: TextStyle(
                  color: resolved
                      ? MonstruoTheme.onSurfaceDim
                      : MonstruoTheme.warning,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (entry.hitlAction != null) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: MonstruoTheme.background,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    entry.hitlAction!,
                    style: const TextStyle(
                      color: MonstruoTheme.onSurfaceDim,
                      fontFamily: 'monospace',
                      fontSize: 10.5,
                    ),
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 8),
          Text(
            entry.text,
            style: const TextStyle(
              color: MonstruoTheme.onBackground,
              fontSize: 13.5,
              height: 1.4,
            ),
          ),
          if (entry.hitlPayload != null && entry.hitlPayload!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: MonstruoTheme.background,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                entry.hitlPayload!.length > 320
                    ? '${entry.hitlPayload!.substring(0, 320)}…'
                    : entry.hitlPayload!,
                style: const TextStyle(
                  color: MonstruoTheme.onSurfaceDim,
                  fontSize: 11,
                  fontFamily: 'monospace',
                  height: 1.4,
                ),
              ),
            ),
          ],
          const SizedBox(height: 12),
          if (!resolved)
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: onReject,
                    icon: const Icon(Icons.close, size: 16),
                    label: const Text('Rechazar'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: MonstruoTheme.surface,
                      foregroundColor: MonstruoTheme.error,
                      side: const BorderSide(
                          color: MonstruoTheme.error, width: 1),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: onApprove,
                    icon: const Icon(Icons.check, size: 16),
                    label: const Text('Aprobar'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: MonstruoTheme.success,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
              ],
            )
          else
            const Text(
              'Resuelta',
              style: TextStyle(
                color: MonstruoTheme.onSurfaceDim,
                fontSize: 11,
                fontStyle: FontStyle.italic,
              ),
            ),
        ],
      ),
    ).animate().fadeIn(duration: 250.ms).slideX(begin: -0.05, end: 0);
  }
}

// ═══════════════════════════════════════════════════════════════
// S5b — Artifact detection + clickable card
// ═══════════════════════════════════════════════════════════════

/// Un artifact accionable detectado en el output de un tool — típicamente
/// una URL de PR, issue, branch, deploy, archivo de Drive, etc.
class _ArtifactInfo {
  const _ArtifactInfo({
    required this.url,
    required this.label,
    required this.kind,
  });

  final String url;
  final String label;

  /// Categoría visual: pr, issue, branch, deploy, file, link.
  final String kind;
}

/// Patrones canónicos para clasificar URLs.
final _artifactPatterns = <RegExp, String>{
  RegExp(r'github\.com/[^/]+/[^/]+/pull/\d+'): 'pr',
  RegExp(r'github\.com/[^/]+/[^/]+/issues/\d+'): 'issue',
  RegExp(r'github\.com/[^/]+/[^/]+/tree/[\w\-/.]+'): 'branch',
  RegExp(r'github\.com/[^/]+/[^/]+/commit/[a-f0-9]{7,40}'): 'commit',
  RegExp(r'\.(?:up\.)?railway\.app'): 'deploy',
  RegExp(r'vercel\.app'): 'deploy',
  RegExp(r'\.manus\.space'): 'deploy',
  RegExp(r'drive\.google\.com'): 'file',
  RegExp(r'docs\.google\.com'): 'file',
  RegExp(r'notion\.so'): 'doc',
  RegExp(r'supabase\.co/dashboard'): 'db',
};

/// Extrae URLs de un texto y las clasifica.
///
/// Devuelve hasta 5 artefactos para evitar saturar la UI cuando un tool
/// vuelca un dump enorme. Si el output es JSON con campo `url`/`urls`,
/// los respeta como prioritarios.
List<_ArtifactInfo> _detectArtifacts(String? out) {
  if (out == null || out.isEmpty) return const [];
  final results = <_ArtifactInfo>[];
  final seen = <String>{};

  void add(String url, {String? label, String? kind}) {
    final clean = url.trim();
    if (clean.isEmpty || seen.contains(clean)) return;
    if (results.length >= 5) return;
    seen.add(clean);
    final detectedKind = kind ?? _classifyArtifact(clean);
    final detectedLabel =
        label ?? _shortLabelFor(clean, detectedKind);
    results.add(_ArtifactInfo(
      url: clean,
      label: detectedLabel,
      kind: detectedKind,
    ));
  }

  // 1. Si es JSON con campo url/urls, priorizar.
  final trimmed = out.trim();
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      final decoded = jsonDecode(trimmed);
      void walk(dynamic node) {
        if (node is Map) {
          final u = node['url'];
          if (u is String) {
            add(u,
                label: node['label']?.toString() ??
                    node['title']?.toString(),
                kind: node['kind']?.toString());
          }
          for (final v in node.values) {
            walk(v);
          }
        } else if (node is List) {
          for (final v in node) {
            walk(v);
          }
        }
      }

      walk(decoded);
    } catch (_) {
      // ignore: JSON malformado, caemos al regex.
    }
  }

  // 2. Regex genérico de URLs.
  final urlRegex = RegExp(
    r'https?://[^\s\)\]\}<>"\u2018\u2019\u201C\u201D]+',
    caseSensitive: false,
  );
  for (final m in urlRegex.allMatches(out)) {
    add(m.group(0)!);
  }

  return results;
}

String _classifyArtifact(String url) {
  for (final entry in _artifactPatterns.entries) {
    if (entry.key.hasMatch(url)) return entry.value;
  }
  return 'link';
}

String _shortLabelFor(String url, String kind) {
  switch (kind) {
    case 'pr':
      final m = RegExp(r'github\.com/([^/]+)/([^/]+)/pull/(\d+)')
          .firstMatch(url);
      if (m != null) return '${m.group(1)}/${m.group(2)} #${m.group(3)}';
      break;
    case 'issue':
      final m = RegExp(r'github\.com/([^/]+)/([^/]+)/issues/(\d+)')
          .firstMatch(url);
      if (m != null) return '${m.group(1)}/${m.group(2)} #${m.group(3)}';
      break;
    case 'commit':
      final m = RegExp(r'github\.com/([^/]+)/([^/]+)/commit/([a-f0-9]+)')
          .firstMatch(url);
      if (m != null) {
        final sha = m.group(3)!;
        return '${m.group(2)}@${sha.substring(0, sha.length > 7 ? 7 : sha.length)}';
      }
      break;
  }
  // Fallback: dominio + path acortado.
  final uri = Uri.tryParse(url);
  if (uri == null) return url;
  final path = uri.path.length > 28 ? '${uri.path.substring(0, 28)}…' : uri.path;
  return '${uri.host}$path';
}

/// Tarjeta clickable que abre un artifact en el navegador externo.
class _ArtifactCard extends StatelessWidget {
  const _ArtifactCard({
    required this.entry,
    required this.onOpen,
  });

  final _StepEntry entry;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) {
    final kind = entry.artifactKind ?? 'link';
    final iconData = switch (kind) {
      'pr' => Icons.merge_type,
      'issue' => Icons.error_outline,
      'branch' => Icons.account_tree_outlined,
      'commit' => Icons.commit_outlined,
      'deploy' => Icons.rocket_launch_outlined,
      'file' => Icons.insert_drive_file_outlined,
      'doc' => Icons.menu_book_outlined,
      'db' => Icons.storage_outlined,
      _ => Icons.open_in_new,
    };
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(10),
        border: const Border(
          left: BorderSide(color: MonstruoTheme.tertiary, width: 3),
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onOpen,
          borderRadius: BorderRadius.circular(10),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Icon(iconData, size: 18, color: MonstruoTheme.tertiary),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        entry.text,
                        style: const TextStyle(
                          color: MonstruoTheme.onBackground,
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        entry.artifactUrl ?? '',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: MonstruoTheme.onSurfaceDim,
                          fontSize: 11,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                const Icon(
                  Icons.open_in_new,
                  size: 14,
                  color: MonstruoTheme.onSurfaceDim,
                ),
              ],
            ),
          ),
        ),
      ),
    ).animate().fadeIn(duration: 250.ms).slideX(begin: -0.05, end: 0);
  }
}
