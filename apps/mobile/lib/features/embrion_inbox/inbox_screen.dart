/// InboxScreen — Sprint SPR-MOBILE-EMBRION-INBOX-001.
///
/// Cara A (dark) — Línea 1 de la cabina de mando: el iPhone como
/// terminal soberano sobre las propuestas autónomas del Embrión.
///
/// UX:
///   - AppBar con estado del Embrión ("despierto · cycle 42 · $0.01/$30")
///   - Lista de propuestas pending con cards densas (summary, risk, timestamp)
///   - Tap en card → expande payload completo + razones
///   - Botones: Aprobar (verde) / Rechazar (rojo) con haptic + confirm
///   - Pull-to-refresh
///   - Empty state con prosa de identidad
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/mensajeros/embrion_messenger.dart';
import '../../core/theme/brand_dna.dart';
import '../../models/embrion_models.dart';

class EmbrionInboxScreen extends ConsumerWidget {
  const EmbrionInboxScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pending = ref.watch(embrionPendingProposalsProvider);
    final estado = ref.watch(embrionEstadoProvider);

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
          'Bandeja del Embrión',
          style: TextStyle(
            color: MonstruoTheme.onBackground,
            fontSize: 17,
            fontWeight: FontWeight.w600,
            letterSpacing: -0.3,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.refresh_rounded,
              color: MonstruoTheme.onSurfaceDim,
              size: 20,
            ),
            onPressed: () {
              ref.invalidate(embrionPendingProposalsProvider);
              ref.invalidate(embrionEstadoProvider);
              HapticFeedback.lightImpact();
            },
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(38),
          child: _EstadoBar(estado: estado),
        ),
      ),
      body: pending.when(
        loading: () => const _LoadingState(),
        error: (e, _) => _ErrorState(
          message: e.toString(),
          onRetry: () => ref.invalidate(embrionPendingProposalsProvider),
        ),
        data: (proposals) {
          if (proposals.isEmpty) return const _EmptyState();
          return RefreshIndicator(
            color: MonstruoTheme.primary,
            backgroundColor: MonstruoTheme.surface,
            onRefresh: () async {
              ref.invalidate(embrionPendingProposalsProvider);
              ref.invalidate(embrionEstadoProvider);
              await Future.delayed(const Duration(milliseconds: 400));
            },
            child: ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
              itemCount: proposals.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (ctx, i) => _ProposalCard(proposal: proposals[i])
                  .animate()
                  .fadeIn(
                      duration: 300.ms,
                      delay: Duration(milliseconds: i * 40))
                  .slideY(begin: 0.05, end: 0),
            ),
          );
        },
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// EstadoBar — header con pulso del Embrión
// ═══════════════════════════════════════════════════════════════

class _EstadoBar extends StatelessWidget {
  const _EstadoBar({required this.estado});
  final AsyncValue<EmbrionEstado> estado;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 38,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: const BoxDecoration(
        color: MonstruoTheme.surface,
        border: Border(
          bottom: BorderSide(color: MonstruoTheme.divider, width: 0.5),
        ),
      ),
      child: estado.when(
        loading: () => Row(
          children: const [
            _PulseDot(color: MonstruoTheme.onSurfaceDim),
            SizedBox(width: 8),
            Text('Consultando estado…',
                style: TextStyle(
                    color: MonstruoTheme.onSurfaceDim, fontSize: 12)),
          ],
        ),
        error: (_, __) => Row(
          children: const [
            _PulseDot(color: MonstruoTheme.error),
            SizedBox(width: 8),
            Text('Estado no disponible',
                style: TextStyle(
                    color: MonstruoTheme.onSurfaceDim, fontSize: 12)),
          ],
        ),
        data: (e) => Row(
          children: [
            _PulseDot(
              color: e.running ? MonstruoTheme.success : MonstruoTheme.warning,
            ),
            const SizedBox(width: 8),
            Text(
              e.running ? 'Despierto' : 'Dormido',
              style: const TextStyle(
                color: MonstruoTheme.onBackground,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              '· ciclo ${e.cycleCount}',
              style: const TextStyle(
                  color: MonstruoTheme.onSurfaceDim, fontSize: 12),
            ),
            const Spacer(),
            Text(
              '\$${e.costTodayUsd.toStringAsFixed(2)} / \$${e.dailyBudgetUsd.toStringAsFixed(0)}',
              style: const TextStyle(
                color: MonstruoTheme.onSurfaceDim,
                fontSize: 11,
                fontFeatures: [FontFeature.tabularFigures()],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PulseDot extends StatelessWidget {
  const _PulseDot({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        boxShadow: [
          BoxShadow(color: color.withValues(alpha: 0.5), blurRadius: 6),
        ],
      ),
    )
        .animate(onPlay: (c) => c.repeat())
        .fadeIn(duration: 800.ms)
        .then()
        .fadeOut(duration: 800.ms);
  }
}

// ═══════════════════════════════════════════════════════════════
// ProposalCard — card individual con expand + acciones
// ═══════════════════════════════════════════════════════════════

class _ProposalCard extends ConsumerStatefulWidget {
  const _ProposalCard({required this.proposal});
  final EmbrionProposal proposal;

  @override
  ConsumerState<_ProposalCard> createState() => _ProposalCardState();
}

class _ProposalCardState extends ConsumerState<_ProposalCard> {
  bool _expanded = false;
  bool _busy = false;

  Color get _riskColor {
    switch (widget.proposal.riskLevel) {
      case ProposalRisk.low:
        return MonstruoTheme.success;
      case ProposalRisk.medium:
        return MonstruoTheme.primary;
      case ProposalRisk.high:
        return MonstruoTheme.warning;
      case ProposalRisk.critical:
        return MonstruoTheme.error;
      case ProposalRisk.unknown:
        return MonstruoTheme.onSurfaceDim;
    }
  }

  String get _ageLabel {
    final delta = DateTime.now().difference(widget.proposal.createdAt);
    if (delta.inMinutes < 1) return 'ahora';
    if (delta.inHours < 1) return 'hace ${delta.inMinutes}m';
    if (delta.inDays < 1) return 'hace ${delta.inHours}h';
    return DateFormat('dd MMM HH:mm', 'es').format(widget.proposal.createdAt);
  }

  Future<void> _approve() async {
    if (_busy) return;
    HapticFeedback.mediumImpact();
    setState(() => _busy = true);
    try {
      final m = ref.read(embrionMessengerProvider);
      await m.approveProposal(widget.proposal.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Aprobada. El kernel la ejecutará.'),
          backgroundColor: MonstruoTheme.surfaceElevated,
          duration: Duration(seconds: 2),
        ));
        ref.invalidate(embrionPendingProposalsProvider);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('No se pudo aprobar: $e'),
          backgroundColor: MonstruoTheme.error,
        ));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _reject() async {
    if (_busy) return;
    HapticFeedback.mediumImpact();
    final reason = await showDialog<String>(
      context: context,
      builder: (ctx) => const _RejectDialog(),
    );
    if (reason == null || reason.isEmpty) return;
    setState(() => _busy = true);
    try {
      final m = ref.read(embrionMessengerProvider);
      await m.rejectProposal(widget.proposal.id, reason: reason);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Rechazada.'),
          backgroundColor: MonstruoTheme.surfaceElevated,
        ));
        ref.invalidate(embrionPendingProposalsProvider);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('No se pudo rechazar: $e'),
          backgroundColor: MonstruoTheme.error,
        ));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.proposal;
    return GestureDetector(
      onTap: () {
        HapticFeedback.selectionClick();
        setState(() => _expanded = !_expanded);
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 220),
        curve: Curves.easeOutCubic,
        decoration: BoxDecoration(
          color: MonstruoTheme.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: MonstruoTheme.divider.withValues(alpha: 0.6),
            width: 0.5,
          ),
        ),
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _riskColor,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  p.proposalType.toUpperCase(),
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.8,
                    color: _riskColor,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '· riesgo ${p.riskLevel.label.toLowerCase()}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
                const Spacer(),
                Text(
                  _ageLabel,
                  style: const TextStyle(
                    fontSize: 11,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            // Summary
            Text(
              p.summary,
              maxLines: _expanded ? null : 3,
              overflow: _expanded ? null : TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 14.5,
                height: 1.4,
                color: MonstruoTheme.onBackground,
              ),
            ),
            // Payload expanded
            if (_expanded && p.payload.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: MonstruoTheme.background,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: MonstruoTheme.divider.withValues(alpha: 0.4),
                    width: 0.5,
                  ),
                ),
                child: Text(
                  _prettyPayload(p.payload),
                  style: const TextStyle(
                    fontSize: 12,
                    fontFamily: 'monospace',
                    color: MonstruoTheme.onSurfaceDim,
                    height: 1.5,
                  ),
                ),
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Text(
                    'Por: ${p.proposedBy}',
                    style: const TextStyle(
                      fontSize: 11,
                      color: MonstruoTheme.onSurfaceDim,
                    ),
                  ),
                  if (p.cycleId != null) ...[
                    const Text('  ·  ',
                        style: TextStyle(color: MonstruoTheme.onSurfaceDim)),
                    Text(
                      'Ciclo ${p.cycleId}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: MonstruoTheme.onSurfaceDim,
                      ),
                    ),
                  ],
                ],
              ),
            ],
            const SizedBox(height: 12),
            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _busy ? null : _reject,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: MonstruoTheme.error,
                      side: BorderSide(
                        color: MonstruoTheme.error.withValues(alpha: 0.4),
                      ),
                      padding:
                          const EdgeInsets.symmetric(vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    icon: const Icon(Icons.close_rounded, size: 16),
                    label: const Text('Rechazar',
                        style: TextStyle(fontSize: 13)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: FilledButton.icon(
                    onPressed: _busy ? null : _approve,
                    style: FilledButton.styleFrom(
                      backgroundColor: MonstruoTheme.success,
                      foregroundColor: Colors.black,
                      padding:
                          const EdgeInsets.symmetric(vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    icon: _busy
                        ? const SizedBox(
                            width: 14,
                            height: 14,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.black,
                            ),
                          )
                        : const Icon(Icons.check_rounded, size: 16),
                    label: const Text('Aprobar',
                        style: TextStyle(
                            fontSize: 13, fontWeight: FontWeight.w600)),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _prettyPayload(Map<String, dynamic> p) {
    final entries = p.entries.take(8);
    return entries.map((e) {
      final v = e.value;
      final vStr =
          v is String ? v : v.toString();
      final truncated =
          vStr.length > 80 ? '${vStr.substring(0, 80)}…' : vStr;
      return '${e.key}: $truncated';
    }).join('\n');
  }
}

// ═══════════════════════════════════════════════════════════════
// Reject dialog (razón obligatoria)
// ═══════════════════════════════════════════════════════════════

class _RejectDialog extends StatefulWidget {
  const _RejectDialog();
  @override
  State<_RejectDialog> createState() => _RejectDialogState();
}

class _RejectDialogState extends State<_RejectDialog> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: MonstruoTheme.surface,
      title: const Text('¿Por qué rechazar?',
          style: TextStyle(color: MonstruoTheme.onBackground, fontSize: 17)),
      content: TextField(
        controller: _ctrl,
        autofocus: true,
        maxLines: 3,
        style: const TextStyle(color: MonstruoTheme.onBackground),
        decoration: InputDecoration(
          hintText: 'Razón (mín. 1 carácter)',
          hintStyle: const TextStyle(color: MonstruoTheme.onSurfaceDim),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide:
                BorderSide(color: MonstruoTheme.divider.withValues(alpha: 0.5)),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancelar',
              style: TextStyle(color: MonstruoTheme.onSurfaceDim)),
        ),
        FilledButton(
          style: FilledButton.styleFrom(
            backgroundColor: MonstruoTheme.error,
          ),
          onPressed: () => Navigator.pop(context, _ctrl.text.trim()),
          child: const Text('Rechazar'),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// Empty / Loading / Error states
// ═══════════════════════════════════════════════════════════════

class _EmptyState extends StatelessWidget {
  const _EmptyState();
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.inbox_outlined,
              size: 56,
              color: MonstruoTheme.onSurfaceDim,
            ),
            const SizedBox(height: 16),
            const Text(
              'Sin propuestas pendientes',
              style: TextStyle(
                color: MonstruoTheme.onBackground,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'El Embrión observa, piensa y propone solo cuando la realidad lo amerita. Tu bandeja vacía es señal de calma — no de inactividad.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: MonstruoTheme.onSurfaceDim,
                fontSize: 13,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LoadingState extends StatelessWidget {
  const _LoadingState();
  @override
  Widget build(BuildContext context) {
    return const Center(
      child: CircularProgressIndicator(
        color: MonstruoTheme.primary,
        strokeWidth: 2,
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off_rounded,
                color: MonstruoTheme.error, size: 48),
            const SizedBox(height: 12),
            const Text('No pude leer el inbox del Embrión.',
                style: TextStyle(
                    color: MonstruoTheme.onBackground, fontSize: 14)),
            const SizedBox(height: 4),
            Text(message,
                textAlign: TextAlign.center,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                    color: MonstruoTheme.onSurfaceDim, fontSize: 12)),
            const SizedBox(height: 16),
            OutlinedButton(
              onPressed: onRetry,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      ),
    );
  }
}
