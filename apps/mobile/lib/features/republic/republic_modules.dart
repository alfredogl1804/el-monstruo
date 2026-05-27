/// Catálogo canónico de los 13 módulos federados de Cognitive Republic.
///
/// Cada módulo tiene: id, nombre, ícono, ruta GoRouter, descripción.
/// Este catálogo es la fuente única de verdad para navegación + breadcrumbs.
library;

import 'package:flutter/material.dart';

class RepublicModule {
  final String id;
  final String name;
  final String shortName;
  final IconData icon;
  final String route;
  final String tagline;
  final String quadrant; // 'soberana', 'gobernanza', 'operativa', 'continuidad'

  const RepublicModule({
    required this.id,
    required this.name,
    required this.shortName,
    required this.icon,
    required this.route,
    required this.tagline,
    required this.quadrant,
  });
}

/// Los 13 módulos federados según rediseño v2 ChatGPT (DSC-G-019).
class RepublicModules {
  RepublicModules._();

  static const List<RepublicModule> all = [
    // ─── Trilogía Soberana (3) ───
    RepublicModule(
      id: 'forge-constellation',
      name: 'Forja Constellation',
      shortName: 'Constellation',
      icon: Icons.hub_outlined,
      route: '/republic/constellation',
      tagline: 'Mapa vivo de la república: 12 nodos federados.',
      quadrant: 'soberana',
    ),
    RepublicModule(
      id: 'sovereign-time-axis',
      name: 'Sovereign Time Axis',
      shortName: 'Time Axis',
      icon: Icons.timeline_outlined,
      route: '/republic/timeline',
      tagline: 'Línea civilizacional: DSCs, sprints, P0s, milestones.',
      quadrant: 'soberana',
    ),
    RepublicModule(
      id: 'cognitive-pnl',
      name: 'Cognitive P&L',
      shortName: 'P&L',
      icon: Icons.show_chart_outlined,
      route: '/republic/pnl',
      tagline: 'Economía cognitiva: cost burn, throughput, sovereignty score.',
      quadrant: 'soberana',
    ),

    // ─── Cuadrante Gobernanza (4) ───
    RepublicModule(
      id: 'sovereign-envelope-mesh',
      name: 'Sovereign Envelope Mesh',
      shortName: 'Envelope Mesh',
      icon: Icons.shield_outlined,
      route: '/republic/envelope-mesh',
      tagline: 'Sobres firmados Ed25519 cruzando el ecosistema.',
      quadrant: 'gobernanza',
    ),
    RepublicModule(
      id: 'reality-diff-theater',
      name: 'Reality Diff Theater',
      shortName: 'Reality Diff',
      icon: Icons.compare_outlined,
      route: '/republic/reality-diff',
      tagline: 'Declarado vs vivo: drift entre genoma y producción.',
      quadrant: 'gobernanza',
    ),
    RepublicModule(
      id: 'doctrine-court',
      name: 'Doctrine Court',
      shortName: 'Doctrine',
      icon: Icons.gavel_outlined,
      route: '/republic/doctrine',
      tagline: 'Capilla de DSCs: doctrina firmada por T1.',
      quadrant: 'gobernanza',
    ),
    RepublicModule(
      id: 'forge-genesis-kit',
      name: 'Forge Genesis Kit',
      shortName: 'Genesis Kit',
      icon: Icons.token_outlined,
      route: '/republic/genesis-kit',
      tagline: 'Manifestaciones públicas de la república.',
      quadrant: 'gobernanza',
    ),

    // ─── Cuadrante Operativa (3) ───
    RepublicModule(
      id: 'embryo-industrial-grid',
      name: 'Embryo Industrial Grid',
      shortName: 'Embryo Grid',
      icon: Icons.psychology_outlined,
      route: '/republic/embryo-grid',
      tagline: '9 embriones Python vivos en líneas de producción.',
      quadrant: 'operativa',
    ),
    RepublicModule(
      id: 'cognitive-republic-registry',
      name: 'Cognitive Republic Registry',
      shortName: 'Registry',
      icon: Icons.account_tree_outlined,
      route: '/republic/registry',
      tagline: '103 repos + 19 servicios + 287 tablas + 34 skills.',
      quadrant: 'operativa',
    ),
    RepublicModule(
      id: 'power-lane-scaler',
      name: 'Power Lane Scaler',
      shortName: 'Power Lanes',
      icon: Icons.speed_outlined,
      route: '/republic/power-lanes',
      tagline: 'L0–L6: enrutamiento por capacidad y soberanía.',
      quadrant: 'operativa',
    ),

    // ─── Cuadrante Continuidad (3) ───
    RepublicModule(
      id: 'mission-capsule-conveyor',
      name: 'Mission Capsule Conveyor',
      shortName: 'Missions',
      icon: Icons.local_shipping_outlined,
      route: '/republic/missions',
      tagline: 'Cápsulas atómicas firmadas, ciclos de iteración.',
      quadrant: 'continuidad',
    ),
    RepublicModule(
      id: 'evidence-receipt-vault',
      name: 'Evidence Receipt Vault',
      shortName: 'Receipts',
      icon: Icons.receipt_long_outlined,
      route: '/republic/receipts',
      tagline: 'Recibos verificables: cada acción tiene evidencia.',
      quadrant: 'continuidad',
    ),
    RepublicModule(
      id: 'omega-command-theater',
      name: 'Omega Command Theater',
      shortName: 'Omega',
      icon: Icons.theaters_outlined,
      route: '/republic/omega',
      tagline: 'Vitrina monumental: la república visible.',
      quadrant: 'continuidad',
    ),
  ];

  static RepublicModule? byId(String id) {
    try {
      return all.firstWhere((m) => m.id == id);
    } catch (_) {
      return null;
    }
  }

  static List<RepublicModule> byQuadrant(String q) =>
      all.where((m) => m.quadrant == q).toList();
}
