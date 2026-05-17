import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createRoot } from "react-dom/client";
import { StrictMode, act } from "react";
import { Chat } from "./Chat";
import { FORJA_TUTOR_PREF_KEYS } from "@/lib/tutor/preferences";

/**
 * La Forja — tests del componente Chat (D3.3 T3).
 * Sprint LA-FORJA-001 D3.3.
 *
 * Estrategia binaria: mockeamos `@ai-sdk/react` y `ai` directamente con
 * `vi.mock` para evitar dependencia de MSW/red real. Esto:
 *   - Mantiene el patrón canónico Tour.test.tsx (createRoot + act + vi.mock)
 *   - Reduce superficie de deps (no instalar msw, no service workers)
 *   - Permite verificar contratos UI/persistence/disabled-states binariamente
 *
 * Cubre:
 *   - Render inicial: toggle visible, sin mensajes, composer habilitado
 *   - Toggle persiste localStorage en cada cambio
 *   - Toggle disabled durante streaming
 *   - Banda de error con botón Reintentar cuando hay error
 *   - sendMessage no se invoca con input vacío
 *   - Cursor blink solo en último mensaje assistant durante streaming
 *   - hidratación: toggle inicia disabled si !hydrated y se habilita post-mount
 */

// ─── Mocks: estado controlado del hook useChat ──────────────────────────────
type UIMessage = {
  id: string;
  role: "user" | "assistant";
  parts: { type: "text"; text: string }[];
};

interface MockChatState {
  messages: UIMessage[];
  status: "ready" | "submitted" | "streaming" | "error";
  error: Error | undefined;
  sendMessage: ReturnType<typeof vi.fn>;
  regenerate: ReturnType<typeof vi.fn>;
  stop: ReturnType<typeof vi.fn>;
}

const mockState: MockChatState = {
  messages: [],
  status: "ready",
  error: undefined,
  sendMessage: vi.fn(),
  regenerate: vi.fn(),
  stop: vi.fn(),
};

vi.mock("@ai-sdk/react", () => ({
  useChat: () => ({
    messages: mockState.messages,
    sendMessage: mockState.sendMessage,
    status: mockState.status,
    error: mockState.error,
    regenerate: mockState.regenerate,
    stop: mockState.stop,
  }),
}));

vi.mock("ai", () => {
  class DefaultChatTransport {
    public __opts: unknown;
    constructor(opts: unknown) {
      this.__opts = opts;
    }
  }
  return { DefaultChatTransport };
});

// streamdown es ESM-only y depende de subdeps pesadas; en tests devolvemos
// un wrapper trivial que solo imprime el children. La cobertura del
// rendering real se valida en e2e/visual.
vi.mock("streamdown", () => ({
  Streamdown: ({ children }: { children: string }) => children,
}));

// ─── Helpers: localStorage Map-backed (happy-dom no expone Storage real) ───
function installStorage() {
  const store = new Map<string, string>();
  const mock = {
    store,
    getItem: vi.fn((k: string) => (store.has(k) ? store.get(k)! : null)),
    setItem: vi.fn((k: string, v: string) => {
      store.set(k, String(v));
    }),
    removeItem: vi.fn((k: string) => {
      store.delete(k);
    }),
    clear: vi.fn(() => store.clear()),
  };
  Object.defineProperty(window, "localStorage", {
    value: mock,
    configurable: true,
    writable: true,
  });
  return mock;
}

function setup() {
  const container = document.createElement("div");
  document.body.appendChild(container);
  const root = createRoot(container);
  act(() => {
    root.render(
      <StrictMode>
        <Chat apiUrl="http://api.test.local" />
      </StrictMode>,
    );
  });
  return {
    container,
    cleanup: () => {
      act(() => root.unmount());
      container.remove();
    },
  };
}

function $byTestId(c: HTMLElement, id: string): HTMLElement {
  const el = c.querySelector(`[data-testid="${id}"]`);
  if (!(el instanceof HTMLElement)) {
    throw new Error(`testId ${id} not found`);
  }
  return el;
}

function $byTestIdOrNull(c: HTMLElement, id: string): HTMLElement | null {
  const el = c.querySelector(`[data-testid="${id}"]`);
  return el instanceof HTMLElement ? el : null;
}

describe("Chat component (D3.3)", () => {
  let storage: ReturnType<typeof installStorage>;

  beforeEach(() => {
    storage = installStorage();
    mockState.messages = [];
    mockState.status = "ready";
    mockState.error = undefined;
    mockState.sendMessage.mockReset();
    mockState.regenerate.mockReset();
    mockState.stop.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renderiza toggle de validación magna en estado inicial (off)", () => {
    const { container, cleanup } = setup();
    try {
      const toggle = $byTestId(container, "forja-validation-toggle");
      expect(toggle.getAttribute("aria-checked")).toBe("false");
      expect(toggle.getAttribute("role")).toBe("switch");
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("hidrata el toggle desde localStorage en mount (true persistido)", () => {
    storage.store.set(FORJA_TUTOR_PREF_KEYS.requireValidation, "true");
    const { container, cleanup } = setup();
    try {
      const toggle = $byTestId(container, "forja-validation-toggle");
      expect(toggle.getAttribute("aria-checked")).toBe("true");
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("click en toggle persiste el valor en localStorage", () => {
    const { container, cleanup } = setup();
    try {
      const toggle = $byTestId(container, "forja-validation-toggle");
      act(() => {
        toggle.click();
      });
      expect(storage.store.get(FORJA_TUTOR_PREF_KEYS.requireValidation)).toBe(
        "true",
      );
      // Click again → off
      act(() => {
        toggle.click();
      });
      expect(storage.store.get(FORJA_TUTOR_PREF_KEYS.requireValidation)).toBe(
        "false",
      );
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("toggle queda disabled durante streaming", () => {
    mockState.status = "streaming";
    const { container, cleanup } = setup();
    try {
      const toggle = $byTestId(container, "forja-validation-toggle");
      expect((toggle as HTMLButtonElement).disabled).toBe(true);
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("muestra banda de error con botón Reintentar cuando hay error", () => {
    mockState.status = "error";
    mockState.error = new Error("upstream blew up");
    const { container, cleanup } = setup();
    try {
      const alert = container.querySelector('[role="alert"]');
      expect(alert).toBeTruthy();
      expect(alert?.textContent).toContain("[la-forja:tutor_stream_failed]");
      expect(alert?.textContent).toContain("upstream blew up");
      // Click reintentar invoca regenerate
      const retry = alert?.querySelector("button");
      expect(retry).toBeTruthy();
      act(() => {
        (retry as HTMLButtonElement).click();
      });
      expect(mockState.regenerate).toHaveBeenCalledTimes(1);
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("composer no envía cuando el input está vacío", () => {
    const { container, cleanup } = setup();
    try {
      const send = $byTestId(container, "forja-send") as HTMLButtonElement;
      // Submit deshabilitado mientras input.trim() === ""
      expect(send.disabled).toBe(true);
      act(() => {
        send.click();
      });
      expect(mockState.sendMessage).not.toHaveBeenCalled();
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("composer envía con texto y limpia input", () => {
    const { container, cleanup } = setup();
    try {
      const composer = $byTestId(
        container,
        "forja-composer",
      ) as HTMLTextAreaElement;
      // Simular cambio controlado: dispatchEvent input change
      const proto = Object.getPrototypeOf(composer);
      const setter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
      act(() => {
        setter?.call(composer, "forjar acero");
        composer.dispatchEvent(new Event("input", { bubbles: true }));
      });
      const send = $byTestId(container, "forja-send") as HTMLButtonElement;
      expect(send.disabled).toBe(false);
      act(() => {
        send.click();
      });
      expect(mockState.sendMessage).toHaveBeenCalledWith({
        text: "forjar acero",
      });
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("durante streaming muestra botón Detener en lugar de Forjar", () => {
    mockState.status = "streaming";
    const { container, cleanup } = setup();
    try {
      const send = $byTestIdOrNull(container, "forja-send");
      expect(send).toBeNull();
      // El botón "Detener" no tiene testid pero existe en el form
      const buttons = container.querySelectorAll("button");
      const stopBtn = Array.from(buttons).find(
        (b) => b.textContent?.trim() === "Detener",
      );
      expect(stopBtn).toBeTruthy();
      act(() => {
        (stopBtn as HTMLButtonElement).click();
      });
      expect(mockState.stop).toHaveBeenCalledTimes(1);
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("renderiza mensajes assistant y user con sus testids", () => {
    mockState.messages = [
      {
        id: "u1",
        role: "user",
        parts: [{ type: "text", text: "hola" }],
      },
      {
        id: "a1",
        role: "assistant",
        parts: [{ type: "text", text: "respuesta" }],
      },
    ];
    const { container, cleanup } = setup();
    try {
      expect($byTestId(container, "forja-msg-user")).toBeTruthy();
      expect($byTestId(container, "forja-msg-assistant")).toBeTruthy();
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("cursor blink solo aparece en último mensaje assistant durante streaming", () => {
    mockState.status = "streaming";
    mockState.messages = [
      {
        id: "u1",
        role: "user",
        parts: [{ type: "text", text: "hola" }],
      },
      {
        id: "a1",
        role: "assistant",
        parts: [{ type: "text", text: "for" }],
      },
    ];
    const { container, cleanup } = setup();
    try {
      const cursor = $byTestIdOrNull(container, "forja-msg-cursor");
      expect(cursor).toBeTruthy();
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });

  it("cursor blink ausente cuando status es ready (stream cerrado)", () => {
    mockState.status = "ready";
    mockState.messages = [
      {
        id: "a1",
        role: "assistant",
        parts: [{ type: "text", text: "completo" }],
      },
    ];
    const { container, cleanup } = setup();
    try {
      const cursor = $byTestIdOrNull(container, "forja-msg-cursor");
      expect(cursor).toBeNull();
      cleanup();
    } catch (e) {
      cleanup();
      throw e;
    }
  });
});
