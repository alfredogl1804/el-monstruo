"use client";

import { useRouter } from "next/navigation";
import { useCallback, type ReactNode } from "react";

/**
 * La Forja — wrapper Client Component que inyecta el callback de
 * finish/skip al `Tour`. Vive en su propio archivo para que la
 * página `page.tsx` siga siendo Server Component (mejor para SEO y
 * carga inicial) y solo bajemos JS cuando el usuario interactúa con
 * el tour.
 *
 * Sprint LA-FORJA-001 D3.1.
 */

interface OnboardingFinishHandlerProps {
  children: (
    handleFinish: (result: { skipped: boolean; completedAt: string }) => void,
  ) => ReactNode;
}

export function OnboardingFinishHandler({
  children,
}: OnboardingFinishHandlerProps) {
  const router = useRouter();

  const handleFinish = useCallback(
    (_result: { skipped: boolean; completedAt: string }) => {
      // El cookie ya fue escrito por `Tour`. Redirigimos al landing,
      // que detectará la cookie y mostrará un estado distinto.
      router.push("/");
    },
    [router],
  );

  return <>{children(handleFinish)}</>;
}
