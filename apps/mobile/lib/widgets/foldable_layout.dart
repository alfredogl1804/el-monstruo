import 'package:flutter/material.dart';

import '../core/config.dart';
import '../theme/monstruo_theme.dart';

/// Adaptive layout that detects foldable devices (OPPO Find N5)
/// and provides a dual-pane layout when unfolded.
///
/// When folded (< 600dp): shows single pane (primary)
/// When unfolded (>= 600dp): shows dual pane (primary + detail)
class FoldableLayout extends StatelessWidget {
  const FoldableLayout({
    super.key,
    required this.primaryPane,
    required this.detailPane,
    this.breakpoint = 600,
  });

  final Widget primaryPane;
  final Widget detailPane;
  final double breakpoint;

  @override
  Widget build(BuildContext context) {
    if (!AppConfig.enableFoldableLayout) {
      return primaryPane;
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= breakpoint;

        if (isWide) {
          // Dual pane — OPPO Find N5 unfolded (8.12")
          return Row(
            children: [
              // Primary pane (chat) — 45% width
              Expanded(
                flex: 45,
                child: primaryPane,
              ),
              // Divider
              Container(
                width: 1,
                color: MonstruoTheme.divider,
              ),
              // Detail pane (sandbox/files/genui) — 55% width
              Expanded(
                flex: 55,
                child: detailPane,
              ),
            ],
          );
        }

        // Single pane — folded or regular phone
        return primaryPane;
      },
    );
  }
}

/// Helper to detect if we're in dual-pane mode
class FoldableHelper {
  static bool isDualPane(BuildContext context) {
    return MediaQuery.of(context).size.width >= 600;
  }

  static bool isTabletSize(BuildContext context) {
    return MediaQuery.of(context).size.width >= 768;
  }

  /// Get the display features (hinge position for foldables)
  static List<DisplayFeature> getDisplayFeatures(BuildContext context) {
    return MediaQuery.of(context).displayFeatures;
  }

  /// Check if device has a fold/hinge
  static bool hasFold(BuildContext context) {
    return MediaQuery.of(context).displayFeatures.any(
      (feature) =>
          feature.type == DisplayFeatureType.fold ||
          feature.type == DisplayFeatureType.hinge,
    );
  }
}
