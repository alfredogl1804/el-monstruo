/// Widgets canónicos de Cognitive Republic — paleta Apple/Tesla light.
///
/// Estos widgets son la unidad atómica de UI. Cualquier módulo de los 13
/// debe usarlos para mantener consistencia visual y semántica.
library;

import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/republic_theme.dart';

// ============================================================================
// 1. StatusDot — Pulso vivo de estado (ONLINE / STANDBY / OFFLINE)
// ============================================================================

class StatusDot extends StatefulWidget {
  final String status;
  final double size;
  final bool pulse;

  const StatusDot({
    super.key,
    required this.status,
    this.size = 8,
    this.pulse = true,
  });

  @override
  State<StatusDot> createState() => _StatusDotState();
}

class _StatusDotState extends State<StatusDot>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    );
    if (widget.pulse) _ctrl.repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = RepublicColors.forStatus(widget.status);
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (context, _) {
        final t = _ctrl.value;
        final pulseRadius = widget.size + (t * widget.size * 1.5);
        return SizedBox(
          width: widget.size * 3,
          height: widget.size * 3,
          child: Stack(
            alignment: Alignment.center,
            children: [
              if (widget.pulse)
                Container(
                  width: pulseRadius,
                  height: pulseRadius,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: color.withValues(alpha: (1 - t) * 0.3),
                  ),
                ),
              Container(
                width: widget.size,
                height: widget.size,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

// ============================================================================
// 2. KpiTile — Cluster Tesla: número grande + label minimal
// ============================================================================

class KpiTile extends StatelessWidget {
  final String label;
  final String value;
  final String? unit;
  final String? sublabel;
  final Color? accentColor;
  final IconData? icon;
  final bool isHero;
  final VoidCallback? onTap;

  const KpiTile({
    super.key,
    required this.label,
    required this.value,
    this.unit,
    this.sublabel,
    this.accentColor,
    this.icon,
    this.isHero = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = accentColor ?? RepublicColors.textPrimary;
    final valueStyle = isHero
        ? RepublicTypography.displayMedium.copyWith(color: color)
        : RepublicTypography.headlineLarge.copyWith(color: color);

    final card = Container(
      padding: const EdgeInsets.all(RepublicSpacing.lg),
      decoration: BoxDecoration(
        color: RepublicColors.surface,
        borderRadius: BorderRadius.circular(RepublicRadius.md),
        border: Border.all(color: RepublicColors.hairline, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              if (icon != null) ...[
                Icon(icon, size: 14, color: RepublicColors.textTertiary),
                const SizedBox(width: 6),
              ],
              Text(
                label.toUpperCase(),
                style: RepublicTypography.labelSmall,
              ),
            ],
          ),
          const SizedBox(height: RepublicSpacing.sm),
          RichText(
            text: TextSpan(
              style: valueStyle,
              children: [
                TextSpan(text: value),
                if (unit != null)
                  TextSpan(
                    text: ' $unit',
                    style: RepublicTypography.bodyMedium.copyWith(
                      color: RepublicColors.textSecondary,
                    ),
                  ),
              ],
            ),
          ),
          if (sublabel != null) ...[
            const SizedBox(height: RepublicSpacing.xs),
            Text(sublabel!, style: RepublicTypography.bodySmall),
          ],
        ],
      ),
    );

    if (onTap == null) return card;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          HapticFeedback.lightImpact();
          onTap!();
        },
        borderRadius: BorderRadius.circular(RepublicRadius.md),
        child: card,
      ),
    );
  }
}

// ============================================================================
// 3. SectionHeader — Encabezado canónico con label minúscula tipo cluster
// ============================================================================

class SectionHeader extends StatelessWidget {
  final String label;
  final String? title;
  final String? caption;
  final Widget? trailing;

  const SectionHeader({
    super.key,
    required this.label,
    this.title,
    this.caption,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        RepublicSpacing.lg,
        RepublicSpacing.lg,
        RepublicSpacing.lg,
        RepublicSpacing.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  label.toUpperCase(),
                  style: RepublicTypography.labelSmall,
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
          if (title != null) ...[
            const SizedBox(height: 4),
            Text(title!, style: RepublicTypography.headlineLarge),
          ],
          if (caption != null) ...[
            const SizedBox(height: 4),
            Text(caption!, style: RepublicTypography.bodySmall),
          ],
        ],
      ),
    );
  }
}

// ============================================================================
// 4. NodeCard — Card de nodo federado (usa en Constellation, Embryo, Registry)
// ============================================================================

class NodeCard extends StatelessWidget {
  final String forgeId;
  final String name;
  final String tier;
  final String status;
  final String? subtitle;
  final List<String> tags;
  final VoidCallback? onTap;

  const NodeCard({
    super.key,
    required this.forgeId,
    required this.name,
    required this.tier,
    required this.status,
    this.subtitle,
    this.tags = const [],
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final tierColor = RepublicColors.forTier(tier);

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap == null
            ? null
            : () {
                HapticFeedback.selectionClick();
                onTap!();
              },
        borderRadius: BorderRadius.circular(RepublicRadius.md),
        child: Container(
          padding: const EdgeInsets.all(RepublicSpacing.lg),
          decoration: BoxDecoration(
            color: RepublicColors.surface,
            borderRadius: BorderRadius.circular(RepublicRadius.md),
            border: Border.all(color: RepublicColors.hairline, width: 0.5),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 4,
                    height: 28,
                    decoration: BoxDecoration(
                      color: tierColor,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(width: RepublicSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          name,
                          style: RepublicTypography.headlineSmall,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          forgeId,
                          style: RepublicTypography.monoSmall.copyWith(
                            color: RepublicColors.textTertiary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  StatusDot(status: status),
                ],
              ),
              if (subtitle != null) ...[
                const SizedBox(height: RepublicSpacing.sm),
                Text(subtitle!, style: RepublicTypography.bodySmall),
              ],
              if (tags.isNotEmpty) ...[
                const SizedBox(height: RepublicSpacing.md),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: tags.map((t) => _Pill(label: t)).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  final String label;

  const _Pill({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: RepublicColors.background,
        borderRadius: BorderRadius.circular(RepublicRadius.pill),
        border: Border.all(color: RepublicColors.hairline, width: 0.5),
      ),
      child: Text(
        label,
        style: RepublicTypography.labelSmall.copyWith(
          color: RepublicColors.textSecondary,
        ),
      ),
    );
  }
}

// ============================================================================
// 5. EmptyState — Estado vacío canónico (sin datos / sin auth / error)
// ============================================================================

class EmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget? action;

  const EmptyState({
    super.key,
    required this.icon,
    required this.title,
    this.subtitle,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(RepublicSpacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: RepublicColors.surfaceElevated,
                borderRadius: BorderRadius.circular(RepublicRadius.lg),
                border: Border.all(color: RepublicColors.hairline, width: 0.5),
              ),
              child: Icon(icon, color: RepublicColors.textTertiary, size: 24),
            ),
            const SizedBox(height: RepublicSpacing.lg),
            Text(
              title,
              style: RepublicTypography.headlineSmall,
              textAlign: TextAlign.center,
            ),
            if (subtitle != null) ...[
              const SizedBox(height: RepublicSpacing.sm),
              Text(
                subtitle!,
                style: RepublicTypography.bodyMedium.copyWith(
                  color: RepublicColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
            ],
            if (action != null) ...[
              const SizedBox(height: RepublicSpacing.lg),
              action!,
            ],
          ],
        ),
      ),
    );
  }
}

// ============================================================================
// 6. LoadingShimmer — Shimmer canónico para estados loading
// ============================================================================

class LoadingShimmer extends StatefulWidget {
  final double height;
  final double? width;
  final BorderRadius? borderRadius;

  const LoadingShimmer({
    super.key,
    this.height = 16,
    this.width,
    this.borderRadius,
  });

  @override
  State<LoadingShimmer> createState() => _LoadingShimmerState();
}

class _LoadingShimmerState extends State<LoadingShimmer>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (context, _) {
        return Container(
          height: widget.height,
          width: widget.width,
          decoration: BoxDecoration(
            borderRadius: widget.borderRadius ??
                BorderRadius.circular(RepublicRadius.sm),
            gradient: LinearGradient(
              colors: [
                RepublicColors.surfaceElevated,
                RepublicColors.surface,
                RepublicColors.surfaceElevated,
              ],
              stops: [
                math.max(0, _ctrl.value - 0.3),
                _ctrl.value,
                math.min(1, _ctrl.value + 0.3),
              ],
            ),
          ),
        );
      },
    );
  }
}

// ============================================================================
// 7. RepublicAppBar — AppBar canónico con título + caption + action
// ============================================================================

class RepublicAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final String? caption;
  final List<Widget> actions;
  final bool showBackButton;

  const RepublicAppBar({
    super.key,
    required this.title,
    this.caption,
    this.actions = const [],
    this.showBackButton = false,
  });

  @override
  Size get preferredSize => Size.fromHeight(caption != null ? 88 : 56);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      automaticallyImplyLeading: showBackButton,
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(title, style: RepublicTypography.headlineMedium),
          if (caption != null)
            Text(
              caption!,
              style: RepublicTypography.bodySmall,
            ),
        ],
      ),
      actions: actions,
    );
  }
}
