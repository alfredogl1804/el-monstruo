/**
 * La Forja — Chat client component (D3.2 SSE).
 *
 * Sprint LA-FORJA-001 D3.2.
 * Doctrina:
 *   - DSC-LF-005: el frontend habla con `/api/tutor/chat` vía SSE
 *     (text/event-stream con UI Message Stream protocol v1).
 *   - Brand DNA: forja al rojo vivo, sin sugerencias de "qué preguntar",
 *     sin chips de prompts, sin disclaimers corporativos.
 *
 * Tecnología:
 *   - useChat de @ai-sdk/react@3.0.186
 *   - DefaultChatTransport contra `${NEXT_PUBLIC_API_URL}/api/tutor/chat`
 *   - El backend retorna headers x-la-forja-{intent,confidence,model,
 *     citations,validation-model} que el cliente consume vía
 *     onResponse para mostrar barra de metadata pre-stream.
 *
 * Estado del input: controlado localmente con useState (no se usa el
 * `input` legacy del hook v2 — fue removido en useChat v3).
 *
 * Errores: el hook expone `error` cuando el stream falla. Lo mostramos
 * con namespace `[la-forja:tutor_*]` y un botón "Reintentar" que llama
 * a `regenerate()`.
 */

"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useMemo, useState } from "react";
import { MessageBubble } from "./MessageBubble";

export interface ChatProps {
  apiUrl: string;
  /** Si true, el backend correrá magna_validation con Sonar antes del stream. */
  requireValidation?: boolean;
}

interface ForjaTutorMetadata {
  intent: string | null;
  confidence: number | null;
  model: string | null;
  citations: string[];
  validationModel: string | null;
}

const EMPTY_META: ForjaTutorMetadata = {
  intent: null,
  confidence: null,
  model: null,
  citations: [],
  validationModel: null,
};

function readMetadataFromHeaders(headers: Headers): ForjaTutorMetadata {
  const intent = headers.get("x-la-forja-intent");
  const confidenceRaw = headers.get("x-la-forja-confidence");
  const model = headers.get("x-la-forja-model");
  const citationsRaw = headers.get("x-la-forja-citations");
  const validationModel = headers.get("x-la-forja-validation-model");

  let citations: string[] = [];
  if (citationsRaw) {
    try {
      const parsed = JSON.parse(citationsRaw);
      if (Array.isArray(parsed)) {
        citations = parsed.filter((c): c is string => typeof c === "string");
      }
    } catch {
      // Header malformado — no rompemos el stream, solo dejamos vacío.
    }
  }

  return {
    intent,
    confidence: confidenceRaw === null ? null : Number(confidenceRaw),
    model,
    citations,
    validationModel,
  };
}

export function Chat({ apiUrl, requireValidation = false }: ChatProps) {
  const [input, setInput] = useState("");
  const [meta, setMeta] = useState<ForjaTutorMetadata>(EMPTY_META);

  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: `${apiUrl}/api/tutor/chat`,
        // Custom fetch: capturamos los headers SSE pre-stream para
        // hidratar la barra de metadata antes de que llegue el primer chunk.
        fetch: async (input, init) => {
          const res = await fetch(input, init);
          if (res.ok) {
            setMeta(readMetadataFromHeaders(res.headers));
          }
          return res;
        },
        // El backend acepta {messages, requireValidation, systemPrompt}.
        // useChat v3 envía `messages` + custom body merge.
        body: { requireValidation },
      }),
    [apiUrl, requireValidation],
  );

  const { messages, sendMessage, status, error, regenerate, stop } = useChat({
    transport,
  });

  const isStreaming = status === "streaming" || status === "submitted";
  const lastMessageId = messages[messages.length - 1]?.id;

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    sendMessage({ text: trimmed });
    setInput("");
  };

  return (
    <div className="flex h-full flex-col gap-4">
      {/* Metadata bar — visible solo cuando hay datos del último turn */}
      {(meta.intent !== null || meta.citations.length > 0) && (
        <div
          className="flex flex-wrap gap-x-6 gap-y-1 border border-acero-700 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.2em] text-acero-500"
          style={{ borderRadius: "var(--radius-forja)" }}
          data-testid="forja-meta-bar"
        >
          {meta.intent && (
            <span>
              intent: <span className="text-forja-300">{meta.intent}</span>
              {meta.confidence !== null && (
                <span className="text-graphite-500">
                  {" "}
                  ({meta.confidence.toFixed(2)})
                </span>
              )}
            </span>
          )}
          {meta.model && (
            <span>
              modelo: <span className="text-forja-300">{meta.model}</span>
            </span>
          )}
          {meta.validationModel && (
            <span>
              magna:{" "}
              <span className="text-forja-300">{meta.validationModel}</span>
            </span>
          )}
          {meta.citations.length > 0 && (
            <span>
              citas:{" "}
              <span className="text-forja-300">{meta.citations.length}</span>
            </span>
          )}
        </div>
      )}

      {/* Lista de mensajes */}
      <div
        className="flex-1 overflow-y-auto flex flex-col gap-6 pr-2"
        data-testid="forja-messages"
      >
        {messages.length === 0 && (
          <p className="text-acero-500 font-mono text-xs">
            Escribe lo que necesitas forjar. El tutor responde con disciplina
            binaria.
          </p>
        )}
        {messages.map((m) => (
          <MessageBubble
            key={m.id}
            message={m}
            isStreaming={isStreaming && m.id === lastMessageId}
          />
        ))}
      </div>

      {/* Citations footer cuando aplica */}
      {meta.citations.length > 0 && (
        <details
          className="border border-acero-700 px-3 py-2"
          style={{ borderRadius: "var(--radius-forja)" }}
        >
          <summary className="cursor-pointer font-mono text-[10px] uppercase tracking-[0.2em] text-acero-500">
            Fuentes ({meta.citations.length})
          </summary>
          <ul className="mt-2 flex flex-col gap-1 font-mono text-xs">
            {meta.citations.map((url) => (
              <li key={url}>
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-forja-300 hover:text-forja-500 underline-offset-2 hover:underline break-all"
                >
                  {url}
                </a>
              </li>
            ))}
          </ul>
        </details>
      )}

      {/* Error namespace */}
      {error && (
        <div
          role="alert"
          className="border border-forja-600 bg-graphite-900 px-3 py-2 font-mono text-xs text-forja-300"
          style={{ borderRadius: "var(--radius-forja)" }}
        >
          [la-forja:tutor_stream_failed] {error.message}
          <button
            type="button"
            onClick={() => regenerate()}
            className="ml-3 border border-forja-500 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] hover:bg-forja-500 hover:text-graphite-900"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Composer */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex gap-2"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Escribe aquí. Enter envía, Shift+Enter salta línea."
          rows={2}
          className="flex-1 resize-none border border-acero-700 bg-graphite-900 px-3 py-2 font-mono text-sm text-graphite-100 placeholder:text-graphite-500 focus:border-forja-500 focus:outline-none"
          style={{ borderRadius: "var(--radius-forja)" }}
          disabled={isStreaming}
          data-testid="forja-composer"
        />
        {isStreaming ? (
          <button
            type="button"
            onClick={() => stop()}
            className="border border-forja-500 px-4 py-2 font-mono text-xs uppercase tracking-[0.2em] text-forja-300 hover:bg-forja-500 hover:text-graphite-900"
            style={{ borderRadius: "var(--radius-forja)" }}
          >
            Detener
          </button>
        ) : (
          <button
            type="submit"
            disabled={input.trim().length === 0}
            className="border border-forja-500 bg-forja-500 px-4 py-2 font-mono text-xs uppercase tracking-[0.2em] text-graphite-900 hover:bg-forja-600 disabled:cursor-not-allowed disabled:opacity-40"
            style={{ borderRadius: "var(--radius-forja)" }}
            data-testid="forja-send"
          >
            Forjar
          </button>
        )}
      </form>
    </div>
  );
}
