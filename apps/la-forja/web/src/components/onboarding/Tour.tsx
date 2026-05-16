"use client";

import { useCallback, useState } from "react";
import { StepShell } from "./StepShell";
import { writeForjaTourCookie } from "@/lib/onboarding/cookie";
import {
  FORJA_TOUR_STEPS,
  FORJA_TOUR_STEP_COUNT,
} from "@/lib/onboarding/steps";

/**
 * La Forja — Tour onboarding (Client Component).
 *
 * Sprint LA-FORJA-001 D3.1.
 *
 * State local del paso, navegación prev/next/skip, persistencia en
 * cookie al completar o saltar, callback `onFinish` para que la
 * página decida a dónde ir después.
 */

interface TourProps {
  /**
   * Llamado cuando el usuario completa o salta el tour. Si `skipped`
   * es `true`, el usuario lo saltó antes del último paso.
   */
  onFinish?: (result: { skipped: boolean; completedAt: string }) => void;
  /**
   * Para tests: inicia en un paso distinto al primero.
   */
  initialIndex?: number;
  /**
   * Para tests: inyecta `Document` (happy-dom) sin tocar el global.
   */
  documentRef?: Document;
}

export function Tour({ onFinish, initialIndex = 0, documentRef }: TourProps) {
  const [index, setIndex] = useState(() =>
    Math.min(Math.max(initialIndex, 0), FORJA_TOUR_STEP_COUNT - 1),
  );

  const step = FORJA_TOUR_STEPS[index];

  const handleNext = useCallback(() => {
    if (index < FORJA_TOUR_STEP_COUNT - 1) {
      setIndex((prev) => prev + 1);
      return;
    }
    const ts = writeForjaTourCookie(
      documentRef ? { documentRef } : {},
    );
    onFinish?.({ skipped: false, completedAt: ts });
  }, [index, onFinish, documentRef]);

  const handlePrev = useCallback(() => {
    setIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  const handleSkip = useCallback(() => {
    const ts = writeForjaTourCookie(
      documentRef ? { documentRef } : {},
    );
    onFinish?.({ skipped: true, completedAt: ts });
  }, [onFinish, documentRef]);

  if (!step) {
    return null;
  }

  const isFirst = index === 0;
  const isLast = index === FORJA_TOUR_STEP_COUNT - 1;

  return (
    <div
      className="mx-auto flex w-full max-w-3xl flex-col gap-6"
      data-testid="forja-tour"
    >
      <StepShell
        step={step}
        index={index}
        total={FORJA_TOUR_STEP_COUNT}
        primaryCta={{ label: step.cta, onClick: handleNext }}
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
