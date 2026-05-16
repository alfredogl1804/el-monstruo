import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "La Forja",
  description:
    "La Forja — herramienta del Monstruo para forjar sprints con disciplina binaria.",
};

export default function ForjaRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
