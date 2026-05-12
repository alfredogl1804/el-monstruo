/// A2UI especializados Monstruo — EmpresaResultCard, LeadCard, ContenidoCard.
///
/// Componentes con semántica fija del dominio del Monstruo, no genéricos.
library;

import 'package:flutter/material.dart';

import '../brand_tokens.dart';
import '../types/a2ui_action.dart';
import '../types/a2ui_node.dart';
import 'actions.dart';
import 'data.dart';

/// Resultado de búsqueda de empresa (pipeline Sprint 87).
/// Props esperadas:
///   - nombre: String
///   - dominio: String? (e.g. "empresa.com")
///   - score: num? (0-100, calidad del match)
///   - sector: String?
///   - ubicacion: String?
///   - resumen: String?
///   - badges: List<{label,variant}>
class A2UIEmpresaResultCard extends StatelessWidget {
  const A2UIEmpresaResultCard({super.key, required this.node, this.dispatcher});

  final A2UINode node;
  final A2UIActionDispatcher? dispatcher;

  @override
  Widget build(BuildContext context) {
    final nombre = node.prop<String>('nombre') ?? 'Empresa';
    final dominio = node.prop<String>('dominio');
    final score = node.prop<num>('score')?.round();
    final sector = node.prop<String>('sector');
    final ubicacion = node.prop<String>('ubicacion');
    final resumen = node.prop<String>('resumen');
    final badges = node.propList('badges');

    return Container(
      decoration: BoxDecoration(
        color: A2UIBrand.graphiteSurface,
        borderRadius: BorderRadius.circular(A2UIBrand.rLg),
        border: Border.all(color: A2UIBrand.border),
      ),
      padding: const EdgeInsets.all(A2UIBrand.s16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(nombre, style: A2UIBrand.titleMd),
                    if (dominio != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 2),
                        child: Text(dominio,
                            style: A2UIBrand.caption
                                .copyWith(color: A2UIBrand.forja)),
                      ),
                  ],
                ),
              ),
              if (score != null) _ScoreBadge(score: score),
            ],
          ),
          if (sector != null || ubicacion != null) ...[
            const SizedBox(height: A2UIBrand.s8),
            Wrap(
              spacing: A2UIBrand.s12,
              runSpacing: A2UIBrand.s4,
              children: [
                if (sector != null)
                  _Meta(icon: Icons.business, value: sector),
                if (ubicacion != null)
                  _Meta(icon: Icons.place_outlined, value: ubicacion),
              ],
            ),
          ],
          if (badges.isNotEmpty) ...[
            const SizedBox(height: A2UIBrand.s8),
            Wrap(
              spacing: A2UIBrand.s4,
              runSpacing: A2UIBrand.s4,
              children: [
                for (final b in badges)
                  A2UIBadge(
                    node: A2UINode(type: 'Badge', props: {
                      'label': b['label']?.toString() ?? '',
                      'variant': b['variant']?.toString() ?? 'neutral',
                    }),
                  ),
              ],
            ),
          ],
          if (resumen != null) ...[
            const SizedBox(height: A2UIBrand.s12),
            Text(resumen, style: A2UIBrand.body),
          ],
          if (node.children.any((c) => c.type == 'Button')) ...[
            const SizedBox(height: A2UIBrand.s12),
            Wrap(
              spacing: A2UIBrand.s8,
              children: [
                for (final c
                    in node.children.where((c) => c.type == 'Button'))
                  A2UIButton(node: c, dispatcher: dispatcher),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  const _ScoreBadge({required this.score});
  final int score;
  @override
  Widget build(BuildContext context) {
    final color = score >= 80
        ? A2UIBrand.success
        : score >= 50
            ? A2UIBrand.warning
            : A2UIBrand.danger;
    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: A2UIBrand.s8, vertical: A2UIBrand.s4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(A2UIBrand.rSm),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text('$score',
          style: A2UIBrand.body
              .copyWith(color: color, fontWeight: FontWeight.w700)),
    );
  }
}

class _Meta extends StatelessWidget {
  const _Meta({required this.icon, required this.value});
  final IconData icon;
  final String value;
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: A2UIBrand.textSecondary),
        const SizedBox(width: A2UIBrand.s4),
        Text(value, style: A2UIBrand.caption),
      ],
    );
  }
}

/// LeadCard: contacto comercial con etapa de embudo + acciones (CTA).
/// Props: nombre, empresa?, etapa (frio|tibio|caliente|cliente), origen?, lastSeen?, score?.
class A2UILeadCard extends StatelessWidget {
  const A2UILeadCard({super.key, required this.node, this.dispatcher});
  final A2UINode node;
  final A2UIActionDispatcher? dispatcher;

  @override
  Widget build(BuildContext context) {
    final nombre = node.prop<String>('nombre') ?? 'Lead';
    final empresa = node.prop<String>('empresa');
    final etapa = node.prop<String>('etapa') ?? 'frio';
    final origen = node.prop<String>('origen');
    final lastSeen = node.prop<String>('lastSeen');
    final score = node.prop<num>('score')?.round();

    final etapaLabel = switch (etapa) {
      'caliente' => 'Caliente',
      'tibio' => 'Tibio',
      'cliente' => 'Cliente',
      _ => 'Frío',
    };

    return Container(
      decoration: BoxDecoration(
        color: A2UIBrand.graphiteSurface,
        borderRadius: BorderRadius.circular(A2UIBrand.rLg),
        border: Border.all(color: A2UIBrand.border),
      ),
      padding: const EdgeInsets.all(A2UIBrand.s16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 18,
                backgroundColor: A2UIBrand.graphite,
                child: Text(
                  nombre.isNotEmpty ? nombre[0].toUpperCase() : '?',
                  style: A2UIBrand.body
                      .copyWith(color: A2UIBrand.forja, fontWeight: FontWeight.w700),
                ),
              ),
              const SizedBox(width: A2UIBrand.s12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(nombre, style: A2UIBrand.titleMd),
                    if (empresa != null)
                      Text(empresa, style: A2UIBrand.caption),
                  ],
                ),
              ),
              A2UIBadge(
                node: A2UINode(type: 'Badge', props: {
                  'label': etapaLabel,
                  'variant': etapa == 'frio'
                      ? 'info'
                      : etapa == 'tibio'
                          ? 'warning'
                          : etapa == 'caliente'
                              ? 'danger'
                              : 'success',
                }),
              ),
            ],
          ),
          if (origen != null || lastSeen != null || score != null) ...[
            const SizedBox(height: A2UIBrand.s12),
            Wrap(
              spacing: A2UIBrand.s16,
              runSpacing: A2UIBrand.s4,
              children: [
                if (origen != null)
                  _Meta(icon: Icons.outbox, value: origen),
                if (lastSeen != null)
                  _Meta(icon: Icons.schedule, value: lastSeen),
                if (score != null)
                  _Meta(
                    icon: Icons.local_fire_department,
                    value: '$score',
                  ),
              ],
            ),
          ],
          if (node.children.any((c) => c.type == 'Button')) ...[
            const SizedBox(height: A2UIBrand.s12),
            Wrap(
              spacing: A2UIBrand.s8,
              children: [
                for (final c
                    in node.children.where((c) => c.type == 'Button'))
                  A2UIButton(node: c, dispatcher: dispatcher),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

/// ContenidoCard: pieza de contenido (artículo, video, hilo X, post LinkedIn).
/// Props: titulo, plataforma?, autor?, fecha?, resumen?, thumbnail?, url?.
class A2UIContenidoCard extends StatelessWidget {
  const A2UIContenidoCard({super.key, required this.node, this.dispatcher});
  final A2UINode node;
  final A2UIActionDispatcher? dispatcher;

  @override
  Widget build(BuildContext context) {
    final titulo = node.prop<String>('titulo') ?? 'Contenido';
    final plataforma = node.prop<String>('plataforma');
    final autor = node.prop<String>('autor');
    final fecha = node.prop<String>('fecha');
    final resumen = node.prop<String>('resumen');
    final thumbnail = node.prop<String>('thumbnail');
    final url = node.prop<String>('url');

    return InkWell(
      onTap: url == null
          ? null
          : () => dispatcher?.call(A2UIAction(
                actionId: node.actionId ?? 'open_contenido',
                sourceWidget: 'ContenidoCard',
                payload: {'url': url, ...?node.actionPayload},
              )),
      borderRadius: BorderRadius.circular(A2UIBrand.rLg),
      child: Container(
        decoration: BoxDecoration(
          color: A2UIBrand.graphiteSurface,
          borderRadius: BorderRadius.circular(A2UIBrand.rLg),
          border: Border.all(color: A2UIBrand.border),
        ),
        padding: const EdgeInsets.all(A2UIBrand.s12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (thumbnail != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(A2UIBrand.rSm),
                child: SizedBox(
                  width: 72,
                  height: 72,
                  child: Image.network(
                    thumbnail,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      color: A2UIBrand.graphite,
                      child:
                          const Icon(Icons.image_not_supported, color: A2UIBrand.acero),
                    ),
                  ),
                ),
              )
            else
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: A2UIBrand.graphite,
                  borderRadius: BorderRadius.circular(A2UIBrand.rSm),
                ),
                child: const Icon(Icons.article_outlined, color: A2UIBrand.forja),
              ),
            const SizedBox(width: A2UIBrand.s12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (plataforma != null)
                    Text(plataforma.toUpperCase(),
                        style: A2UIBrand.caption.copyWith(
                            color: A2UIBrand.forja,
                            letterSpacing: 0.8,
                            fontWeight: FontWeight.w600)),
                  if (plataforma != null) const SizedBox(height: 2),
                  Text(titulo, style: A2UIBrand.titleMd, maxLines: 2,
                      overflow: TextOverflow.ellipsis),
                  if (autor != null || fecha != null) ...[
                    const SizedBox(height: A2UIBrand.s4),
                    Text(
                      [autor, fecha].whereType<String>().join(' · '),
                      style: A2UIBrand.caption,
                    ),
                  ],
                  if (resumen != null) ...[
                    const SizedBox(height: A2UIBrand.s8),
                    Text(resumen,
                        style: A2UIBrand.body,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
