/**
 * La Forja — MessageBubble.
 *
 * Sprint LA-FORJA-001 D3.2.
 * Doctrina: §6 Brand DNA — forja al rojo vivo, sin chatbot amigable.
 *
 * Renderiza un mensaje del chat con tipografía mono para timestamps/role
 * y sans para el cuerpo. User a la derecha con borde forja, assistant a la
 * izquierda con borde acero. Sin avatares, sin emojis, sin gradientes —
 * brutalismo industrial.
 *
 * Streaming: cuando el mensaje aún no termina (status="streaming"), pinta
 * un cursor blink al final del último text part para señalar que sigue
 * forjándose. Ese cursor desaparece cuando el stream cierra.
 */

"use client";

import type { UIMessage } from "ai";

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
          className={`whitespace-pre-wrap px-4 py-3 text-sm leading-relaxed border ${
            isUser
              ? "bg-graphite-700 border-forja-600 text-graphite-100"
              : "bg-graphite-900 border-acero-700 text-graphite-100"
          }`}
          style={{ borderRadius: "var(--radius-forja)" }}
        >
          {text}
          {isStreaming && !isUser && (
            <span
              className="inline-block w-[8px] h-[1em] align-text-bottom bg-forja-500 ml-1 animate-pulse"
              aria-label="forjando"
            />
          )}
        </div>
      </div>
    </div>
  );
}
