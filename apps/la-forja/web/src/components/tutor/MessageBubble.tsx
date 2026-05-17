/**
 * La Forja — MessageBubble.
 *
 * Sprint LA-FORJA-001 D3.2 + D3.3 (markdown rendering).
 * Doctrina:
 *   - §6 Brand DNA — forja al rojo vivo, sin chatbot amigable, sin avatares,
 *     sin emojis, sin gradientes.
 *   - DSC-LF-008 (D3.3): el rendering de markdown del tutor pasa por
 *     `streamdown` (Vercel, Apache-2.0, react^18||^19). Sanitización XSS
 *     activa por default (rehype-sanitize + rehype-harden). Solo los
 *     mensajes del rol "assistant" se renderizan como markdown — el rol
 *     "user" se conserva en `whitespace-pre-wrap` plano (lo que el usuario
 *     escribió, sin transformación).
 *
 * Streaming: el cursor blink se mantiene como sibling fuera de Streamdown
 * y solo se pinta mientras `isStreaming === true && !isUser`.
 */

"use client";

import type { UIMessage } from "ai";
import { Streamdown } from "streamdown";

export interface MessageBubbleProps {
  message: UIMessage;
  isStreaming: boolean;
}

function extractText(message: UIMessage): string {
  // UI Message Parts protocol: parts[].type === "text" → .text
  const parts = message.parts ?? [];
  return parts
    .filter((p): p is { type: "text"; text: string } => p.type === "text")
    .map((p) => p.text)
    .join("");
}

export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const text = extractText(message);

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
      data-testid={`forja-msg-${message.role}`}
    >
      <div
        className={`max-w-[80ch] flex flex-col gap-1 ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        <span
          className={`font-mono text-[10px] tracking-[0.25em] uppercase ${
            isUser ? "text-forja-300" : "text-acero-500"
          }`}
        >
          {isUser ? "Tú" : "Tutor · Claude Opus 4.7"}
        </span>
        <div
          className={`px-4 py-3 text-sm leading-relaxed border ${
            isUser
              ? "bg-graphite-700 border-forja-600 text-graphite-100 whitespace-pre-wrap"
              : "bg-graphite-900 border-acero-700 text-graphite-100"
          }`}
          style={{ borderRadius: "var(--radius-forja)" }}
        >
          {isUser ? (
            text
          ) : (
            <div
              className="forja-markdown"
              data-testid="forja-msg-markdown"
            >
              <Streamdown>{text}</Streamdown>
            </div>
          )}
          {isStreaming && !isUser && (
            <span
              className="inline-block w-[8px] h-[1em] align-text-bottom bg-forja-500 ml-1 animate-pulse"
              aria-label="forjando"
              data-testid="forja-msg-cursor"
            />
          )}
        </div>
      </div>
    </div>
  );
}
