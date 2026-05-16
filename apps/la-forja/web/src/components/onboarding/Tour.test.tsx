import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Tour } from "./Tour";
import {
  clearForjaTourCookie,
  readForjaTourCookie,
} from "@/lib/onboarding/cookie";
import {
  FORJA_TOUR_STEP_COUNT,
  FORJA_TOUR_STEPS,
} from "@/lib/onboarding/steps";
import { createRoot } from "react-dom/client";
import { StrictMode, act } from "react";

/**
 * La Forja — tests del componente Tour.
 * Sprint LA-FORJA-001 D3.1 + hardening Perplexity F-D3.1-04, -11.
 *
 * Estrategia binaria: montamos con `react-dom/client` directo en
 * happy-dom (sin testing-library) para mantener el set de deps mínimo.
 *
 * Hardening aplicado:
 *   F-D3.1-04: nuevo test verifica que doble click rápido en el último
 *              paso solo llama `onFinish` una vez (idempotencia).
 *   F-D3.1-11: tests envuelven `<Tour>` en `<StrictMode>` para cubrir
 *              double-mount de React 19 y race conditions de mount.
 */

// Mock estable de useRouter para evitar dependencia del Next router en
// tests. El test no asserta sobre `redirectTo` directamente; las
// suites posteriores lo cubrirán cuando llegue D3.x.
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

function setup(initialIndex = 0, onFinish = vi.fn()) {
  const container = document.createElement("div");
  document.body.appendChild(container);
  const root = createRoot(container);
  act(() => {
    root.render(
      <StrictMode>
        <Tour onFinish={onFinish} initialIndex={initialIndex} />
      </StrictMode>,
    );
  });
  return {
    container,
    onFinish,
    cleanup: () => {
      act(() => root.unmount());
      container.remove();
    },
  };
}

function clickByTestId(container: HTMLElement, testId: string) {
  const el = container.querySelector(`[data-testid="${testId}"]`);
  if (!(el instanceof HTMLElement)) {
    throw new Error(`testId ${testId} not found`);
  }
  act(() => {
    el.click();
  });
}

describe("Tour component", () => {
  beforeEach(() => {
    mockPush.mockClear();
  });

  afterEach(() => {
    clearForjaTourCookie();
    document.body.innerHTML = "";
  });

  it("renderiza el primer paso al montar", () => {
    const { container, cleanup } = setup();
    const step = container.querySelector("[data-testid='forja-tour-step']");
    expect(step?.getAttribute("data-step-id")).toBe(FORJA_TOUR_STEPS[0]?.id);
    expect(step?.getAttribute("data-step-index")).toBe("0");
    cleanup();
  });

  it("primary CTA avanza al siguiente paso", () => {
    const { container, cleanup } = setup();
    clickByTestId(container, "forja-tour-primary");
    const step = container.querySelector("[data-testid='forja-tour-step']");
    expect(step?.getAttribute("data-step-index")).toBe("1");
    cleanup();
  });

  it("secondary CTA (Anterior) retrocede al paso previo", () => {
    const { container, cleanup } = setup(2);
    clickByTestId(container, "forja-tour-secondary");
    const step = container.querySelector("[data-testid='forja-tour-step']");
    expect(step?.getAttribute("data-step-index")).toBe("1");
    cleanup();
  });

  it("primary CTA en el último paso llama onFinish con skipped=false", () => {
    const onFinish = vi.fn();
    const { container, cleanup } = setup(FORJA_TOUR_STEP_COUNT - 1, onFinish);
    clickByTestId(container, "forja-tour-primary");
    expect(onFinish).toHaveBeenCalledTimes(1);
    expect(onFinish.mock.calls[0]?.[0]?.skipped).toBe(false);
    expect(typeof onFinish.mock.calls[0]?.[0]?.completedAt).toBe("string");
    expect(readForjaTourCookie()).not.toBeNull();
    cleanup();
  });

  it("skip llama onFinish con skipped=true y escribe cookie", () => {
    const onFinish = vi.fn();
    const { container, cleanup } = setup(0, onFinish);
    clickByTestId(container, "forja-tour-skip");
    expect(onFinish).toHaveBeenCalledTimes(1);
    expect(onFinish.mock.calls[0]?.[0]?.skipped).toBe(true);
    expect(readForjaTourCookie()).not.toBeNull();
    cleanup();
  });

  it("primer paso no tiene botón secundario", () => {
    const { container, cleanup } = setup(0);
    expect(
      container.querySelector("[data-testid='forja-tour-secondary']"),
    ).toBeNull();
    cleanup();
  });

  it("último paso no tiene botón skip", () => {
    const { container, cleanup } = setup(FORJA_TOUR_STEP_COUNT - 1);
    expect(
      container.querySelector("[data-testid='forja-tour-skip']"),
    ).toBeNull();
    cleanup();
  });

  // F-D3.1-04: doble click rápido en el último paso solo llama onFinish 1 vez.
  it("doble click rápido en el último paso llama onFinish solo una vez", () => {
    const onFinish = vi.fn();
    const { container, cleanup } = setup(FORJA_TOUR_STEP_COUNT - 1, onFinish);
    clickByTestId(container, "forja-tour-primary");
    clickByTestId(container, "forja-tour-primary");
    clickByTestId(container, "forja-tour-primary");
    expect(onFinish).toHaveBeenCalledTimes(1);
    cleanup();
  });

  // F-D3.1-04: doble skip en el primer paso solo llama onFinish 1 vez.
  it("doble click rápido en skip solo llama onFinish una vez", () => {
    const onFinish = vi.fn();
    const { container, cleanup } = setup(0, onFinish);
    clickByTestId(container, "forja-tour-skip");
    clickByTestId(container, "forja-tour-skip");
    expect(onFinish).toHaveBeenCalledTimes(1);
    cleanup();
  });
});
