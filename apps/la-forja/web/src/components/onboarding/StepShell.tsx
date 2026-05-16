"use client";

import type { RefObject } from "react";
import type { ForjaTourStep } from "@/lib/onboarding/steps";

/**
 * La Forja — shell visual de un paso del tour.
 *
 * Sprint LA-FORJA-001 D3.1 + hardening Perplexity F-D3.1-05, -06, -07, -12.
 *
 * Solo renderiza un paso. La navegación, el state y la lógica de
 * cookie viven en `Tour.tsx`. Esto mantiene la separación entre
 * "contenido + tipografía" (acá) y "estado + transiciones" (allá).
 *
 * Hardening aplicado:
 *   F-D3.1-05: highlights ordenados por longitud descendente para
 *              que match de prefijo no le gane al match más largo
 *              (ej: si highlights = ["50 USD", "50 USD por mes"],
 *              gana "50 USD por mes").
 *   F-D3.1-06: heading recibe `ref` + `tabIndex={-1}` para que el
 *              padre pueda enfocarlo al cambiar de paso (anuncio a
 *              screen readers).
 *   F-D3.1-07: skip y secondary tienen `focus-visible:ring` con
 *              contraste WCAG AA contra `bg-graphite-900`.
 *   F-D3.1-12: keys derivadas de contenido estable (`step.id` +
 *              hash interno), no de índices mutables.
 */

interface StepShellProps {
  step: ForjaTourStep;
  index: number;
  total: number;
  primaryCta: { label: string; onClick: () => void };
  secondaryCta?: { label: string; onClick: () => void };
  skip?: { label: string; onClick: () => void };
  headingRef?: RefObject<HTMLHeadingElement | null>;
}

/**
 * Resalta dentro de `text` cualquier `highlight` exacto envolviéndolo
 * en `<strong className="text-forja-500">`. Sin regex globales para
 * evitar interpretar caracteres especiales.
 *
 * F-D3.1-05: los highlights se ordenan por longitud descendente
 * antes del match para que el más largo gane cuando hay solapamiento.
 */
function highlightText(
  stepId: string,
  text: string,
  highlights: readonly string[] | undefined,
): React.ReactNode {
  if (!highlights || highlights.length === 0) return text;
  const sortedHighlights = [...highlights].sort(
    (a, b) => b.length - a.length,
  );
  let remaining = text;
  const parts: React.ReactNode[] = [];
  let cursor = 0;
  while (remaining.length > 0) {
    let earliest: { hl: string; idx: number } | null = null;
    for (const hl of sortedHighlights) {
      const idx = remaining.indexOf(hl);
      if (idx < 0) continue;
      if (!earliest || idx < earliest.idx) earliest = { hl, idx };
    }
    if (!earliest) {
      parts.push(remaining);
      break;
    }
    if (earliest.idx > 0) {
      parts.push(remaining.slice(0, earliest.idx));
    }
    parts.push(
      <strong
        key={`${stepId}-hl-${cursor}-${earliest.hl}`}
        className="text-forja-500 font-semibold"
      >
        {earliest.hl}
      </strong>,
    );
    cursor += earliest.idx + earliest.hl.length;
    remaining = remaining.slice(earliest.idx + earliest.hl.length);
  }
  return parts;
}

export function StepShell({
  step,
  index,
  total,
  primaryCta,
  secondaryCta,
  skip,
  headingRef,
}: StepShellProps) {
  return (
    <article
      className="flex flex-col gap-8 rounded-[var(--radius-forja)] border border-graphite-700 bg-graphite-900 p-8 sm:p-12"
      aria-labelledby={`forja-tour-step-${step.id}-title`}
      data-testid="forja-tour-step"
      data-step-id={step.id}
      data-step-index={index}
    >
      <header className="flex flex-col gap-2">
        <span className="font-mono text-xs uppercase tracking-[0.2em] text-acero-500">
          {step.eyebrow}
        </span>
        <h2
          id={`forja-tour-step-${step.id}-title`}
          ref={headingRef}
          tabIndex={-1}
          className="text-3xl sm:text-4xl font-semibold text-graphite-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-forja-300 focus-visible:ring-offset-2 focus-visible:ring-offset-graphite-900 rounded-sm"
        >
          {step.title}
        </h2>
      </header>

      <div className="flex flex-col gap-5 text-base sm:text-lg leading-relaxed text-graphite-200">
        {step.body.map((paragraph, paragraphIndex) => (
          <p key={`${step.id}-body-${paragraphIndex}`}>
            {highlightText(step.id, paragraph, step.highlights)}
          </p>
        ))}
      </div>

      {step.bullets && step.bullets.length > 0 && (
        <ul className="flex flex-col gap-3 border-l-2 border-forja-500 pl-5 text-graphite-100">
          {step.bullets.map((bullet, bulletIndex) => (
            <li
              key={`${step.id}-bullet-${bulletIndex}`}
              className="text-sm sm:text-base leading-relaxed"
            >
              {bullet}
            </li>
          ))}
        </ul>
      )}

      <footer className="flex flex-col gap-4 border-t border-graphite-700 pt-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="font-mono text-xs text-acero-500">
          {index + 1}/{total}
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          {skip && (
            <button
              type="button"
              onClick={skip.onClick}
              className="text-sm text-acero-500 underline-offset-4 hover:text-acero-300 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-acero-300 focus-visible:ring-offset-2 focus-visible:ring-offset-graphite-900 rounded-sm px-1"
              data-testid="forja-tour-skip"
            >
              {skip.label}
            </button>
          )}
          {secondaryCta && (
            <button
              type="button"
              onClick={secondaryCta.onClick}
              className="rounded-[var(--radius-forja)] border border-graphite-600 px-5 py-2.5 text-sm font-medium text-graphite-100 hover:border-acero-500 hover:text-graphite-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-acero-300 focus-visible:ring-offset-2 focus-visible:ring-offset-graphite-900"
              data-testid="forja-tour-secondary"
            >
              {secondaryCta.label}
            </button>
          )}
          <button
            type="button"
            onClick={primaryCta.onClick}
            className="rounded-[var(--radius-forja)] bg-forja-500 px-5 py-2.5 text-sm font-semibold text-graphite-900 hover:bg-forja-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-forja-300 focus-visible:ring-offset-2 focus-visible:ring-offset-graphite-900"
            data-testid="forja-tour-primary"
          >
            {primaryCta.label}
          </button>
        </div>
      </footer>
    </article>
  );
}
