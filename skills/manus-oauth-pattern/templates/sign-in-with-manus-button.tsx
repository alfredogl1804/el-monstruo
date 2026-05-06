// El Monstruo — Botón canónico "Sign in with Manus"
// Generado por skill manus-oauth-pattern v0.1.0
//
// DSC-G-004 (Brand Engine): paleta forja inviolable. NUNCA usar primary/secondary.
// Texto exacto: "Sign in with Manus" — NO localizar a "Iniciar sesión con Manus"
// porque la marca Manus se mantiene en inglés global (decisión upstream).

import React from "react";
import { forja, graphite, spacing, radius, textStyle } from "@monstruo/design-tokens";

export interface SignInWithManusButtonProps {
  /** URL de inicio del flow OAuth (default: NEXT_PUBLIC_MANUS_OAUTH_LOGIN_URL) */
  loginUrl?: string;
  /** Después del login, a dónde redirigir (default: window.location.pathname) */
  returnTo?: string;
  /** Variante visual: filled (default, on dark canvas) o outline (on light canvas) */
  variant?: "filled" | "outline";
  /** Tamaño: md (default) o lg */
  size?: "md" | "lg";
  /** Disabled state */
  disabled?: boolean;
  /** Override completo del onClick (raro, mejor dejar el default) */
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
}

const SIZE_STYLES = {
  md: { px: spacing[5], py: spacing[3], font: textStyle.cta },
  lg: { px: spacing[6], py: spacing[4], font: textStyle.headline3 },
};

export const SignInWithManusButton: React.FC<SignInWithManusButtonProps> = ({
  loginUrl = process.env.NEXT_PUBLIC_MANUS_OAUTH_LOGIN_URL,
  returnTo,
  variant = "filled",
  size = "md",
  disabled = false,
  onClick,
}) => {
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (onClick) {
      onClick(e);
      return;
    }
    if (!loginUrl) {
      console.error("auth_login_button_misconfigured: NEXT_PUBLIC_MANUS_OAUTH_LOGIN_URL no definida");
      return;
    }
    const target =
      returnTo ?? (typeof window !== "undefined" ? window.location.pathname : "/");
    const params = new URLSearchParams({
      client_id: process.env.NEXT_PUBLIC_MANUS_OAUTH_CLIENT_ID ?? "",
      redirect_uri: `${window.location.origin}/api/v1/auth/callback`,
      response_type: "code",
      scope: "openid profile email",
      state: encodeURIComponent(target),
    });
    window.location.assign(`${loginUrl}?${params.toString()}`);
  };

  const sizeStyle = SIZE_STYLES[size];

  const baseStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing[2],
    paddingLeft: sizeStyle.px,
    paddingRight: sizeStyle.px,
    paddingTop: sizeStyle.py,
    paddingBottom: sizeStyle.py,
    borderRadius: radius.md,
    fontFamily: sizeStyle.font.fontFamily,
    fontSize: sizeStyle.font.fontSize,
    fontWeight: sizeStyle.font.fontWeight,
    letterSpacing: sizeStyle.font.letterSpacing,
    cursor: disabled ? "not-allowed" : "pointer",
    transition: "all 240ms cubic-bezier(0.16, 0.84, 0.44, 1)",
    border: "none",
    opacity: disabled ? 0.5 : 1,
  };

  const variantStyle: React.CSSProperties =
    variant === "filled"
      ? {
          backgroundColor: forja[500],
          color: graphite[800],
          boxShadow: "0 0 0 1px rgba(249, 115, 22, 0.25), 0 0 16px -4px rgba(249, 115, 22, 0.4)",
        }
      : {
          backgroundColor: "transparent",
          color: forja[500],
          border: `2px solid ${forja[500]}`,
        };

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={handleClick}
      style={{ ...baseStyle, ...variantStyle }}
      aria-label="Sign in with Manus"
    >
      <ManusGlyph size={size === "lg" ? 24 : 18} color={variant === "filled" ? graphite[800] : forja[500]} />
      <span>Sign in with Manus</span>
    </button>
  );
};

// ── Glyph minimalista de Manus (forja icono cuadrado + chispa) ──────
const ManusGlyph: React.FC<{ size: number; color: string }> = ({ size, color }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="3" width="18" height="18" rx="2" stroke={color} strokeWidth="2" />
    <path d="M7 14L12 8L17 14" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="12" cy="17" r="1" fill={color} />
  </svg>
);
