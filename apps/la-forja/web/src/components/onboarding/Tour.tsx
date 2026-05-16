"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { StepShell } from "./StepShell";
import { writeForjaTourCookie } from "@/lib/onboarding/cookie";
import {
  FORJA_TOUR_STEPS,
  FORJA_TOUR_STEP_COUNT,
} from "@/lib/onboarding/steps";

/**
 * La Forja — Tour onboarding (Client Component).
 *
 * Sprint LA-FORJA-001 D3.1 + D3.1 hardening Perplexity F-D3.1-04, -06, -15
 * + D3.1.1 R-D3.1-02 (regression).
 *
 * State local del paso, navegación prev/next/skip, persistencia en
 * cookie al completar o saltar, redirect opcional a `redirectTo`.
 *
 * Hardening aplicado:
 *   F-D3.1-04 + R-D3.1-02: guard de idempotencia.
 *     V1 (D3.1): `if (finished) return` con state cerrado por closure.
 *     Defecto: dos clicks síncronos en el MISMO event loop ven el
 *     mismo `finished=false` y ambos pasan el guard.
 *     V2 (D3.1.1): `useRef<boolean>` mutado sincrónicamente antes de
 *     cualquier side-effect. Un segundo click dentro del mismo task
 *     ve `finishedRef.current=true` y retorna.
 *   F-D3.1-06: aria-live + foco programático al cambiar de paso para
 *              que screen readers anuncien la transición.
 *   F-D3.1-15: useRouter integrado directamente en este Client
 *              Component. Eliminado el wrapper redundante
 *              `OnboardingFinishHandler` (violaba Brand Engine por
 *              el sufijo `Handler`).
 */

interface TourProps {
  /**
   * Llamado cuando el usuario completa o salta el tour. Si `skipped`
   * es `true`, el usuario lo saltó antes del último paso.
   */
  onFinish?: (result: { skipped: boolean; completedAt: string }) => void;
  /**
   * Si está presente, navega a esta ruta tras `onFinish`. Default
   * `undefined` (no navega — útil para tests y para embedding).
   */
  redirectTo?: string;
  /**
   * Para tests: inicia en un paso distinto al primero.
   */
  initialIndex?: number;
  /**
   * Para tests: inyecta `Document` (happy-dom) sin tocar el global.
   */
  documentRef?: Document;
}

export function Tour({
  onFinish,
  redirectTo,
  initialIndex = 0,
  documentRef,
}: TourProps) {
  const router = useRouter();
  const [index, setIndex] = useState(() =>
    Math.min(Math.max(initialIndex, 0), FORJA_TOUR_STEP_COUNT - 1),
  );
  // R-D3.1-02: guard sincrónico via ref. setFinished(true) marca el
  // state para re-render condicional, pero finishedRef es la fuente
  // de verdad para idempotencia.
  const finishedRef = useRef(false);
  const [, setFinished] = useState(false);

  const stepHeadingRef = useRef<HTMLHeadingElement | null>(null);

  const step = FORJA_TOUR_STEPS[index];

  // F-D3.1-06: foco al heading del paso al cambiar de index. Solo
  // mueve foco si ya hubo interacción (no en mount inicial), para no
  // robarle el scroll al usuario que recién aterrizó.
  const isFirstRenderRef = useRef(true);
  useEffect(() => {
    if (isFirstRenderRef.current) {
      isFirstRenderRef.current = false;
      return;
    }
    stepHeadingRef.current?.focus();
  }, [index]);

  const finalize = useCallback(
    (skipped: boolean) => {
      // R-D3.1-02: chequeo + mutación síncrona del ref ANTES de
      // cualquier side-effect. Garantiza que dos invocaciones en el
      // mismo task ven el flag actualizado.
      if (finishedRef.current) return;
      finishedRef.current = true;
      setFinished(true);
      const ts = writeForjaTourCookie(
        documentRef ? { documentRef } : {},
      );
      onFinish?.({ skipped, completedAt: ts });
      if (redirectTo) {
        router.push(redirectTo);
      }
    },
    [onFinish, documentRef, redirectTo, router],
  );

  const handleNext = useCallback(() => {
    if (index < FORJA_TOUR_STEP_COUNT - 1) {
      setIndex((prev) => prev + 1);
      return;
    }
    finalize(false);
  }, [index, finalize]);

  const handlePrev = useCallback(() => {
    setIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  const handleSkip = useCallback(() => {
    finalize(true);
  }, [finalize]);

  if (!step) {
    return null;
  }

  const isFirst = index === 0;
  const isLast = index === FORJA_TOUR_STEP_COUNT - 1;

  return (
    <div
      className="mx-auto flex w-full max-w-3xl flex-col gap-6"
      data-testid="forja-tour"
      aria-live="polite"
      aria-atomic="true"
    >
      <StepShell
        step={step}
        index={index}
        total={FORJA_TOUR_STEP_COUNT}
        primaryCta={{ label: step.cta, onClick: handleNext }}
        headingRef={stepHeadingRef}
        {...(isFirst
          ? {}
          : { secondaryCta: { label: "Anterior", onClick: handlePrev } })}
        {...(isLast
          ? {}
          : { skip: { label: "Saltar tour", onClick: handleSkip } })}
      />
    </div>
  );
}
