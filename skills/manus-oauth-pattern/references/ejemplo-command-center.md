# Ejemplo: Manus-Oauth en Command Center (Next.js 15 App Router)

> El Command Center del Monstruo es la primera consumer de este pattern. Stack: Next.js 15 + Drizzle + TiDB.

---

## Estructura de archivos

```
apps/command-center/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── auth/
│   │           ├── callback/route.ts        ← POST handler usando templates/auth-callback-handler.ts
│   │           ├── logout/route.ts          ← POST clear cookie
│   │           └── me/route.ts              ← GET user actual
│   ├── (auth)/
│   │   ├── login/page.tsx                   ← landing con SignInWithManusButton
│   │   └── link/manus/page.tsx              ← landing del flow Telegram link
│   ├── (protected)/
│   │   ├── layout.tsx                       ← server component: requiere auth
│   │   └── ...
│   └── layout.tsx
├── lib/
│   ├── auth/
│   │   ├── middleware.ts                    ← adaptación de auth-middleware-template.ts
│   │   ├── crypto.ts                        ← AES-256-GCM encrypt/decrypt
│   │   └── session.ts                       ← HMAC sign/verify
│   └── db/
│       └── schema.ts                        ← Drizzle schema con users + user_sessions
└── middleware.ts                            ← Next.js edge middleware
```

---

## `middleware.ts` (edge, runs en cada request)

```typescript
import { NextResponse, type NextRequest } from "next/server";

const PROTECTED_PATHS = ["/dashboard", "/projects", "/settings"];
const PUBLIC_PATHS = ["/login", "/api/v1/auth/callback"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  if (PUBLIC_PATHS.some(p => pathname.startsWith(p))) {
    return NextResponse.next();
  }
  
  const isProtected = PROTECTED_PATHS.some(p => pathname.startsWith(p));
  if (!isProtected) return NextResponse.next();
  
  const cookie = request.cookies.get("monstruo_session")?.value;
  if (!cookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("return_to", pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  // Validación profunda en el route handler. Aquí solo check superficial.
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

---

## `app/api/v1/auth/callback/route.ts`

```typescript
import { NextRequest, NextResponse } from "next/server";
import { handleAuthCallback } from "@/lib/auth/callback-handler";
import { db } from "@/lib/db";
import { encryptToken } from "@/lib/auth/crypto";
import { logger } from "@/lib/logger";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  
  if (!code || !state) {
    return NextResponse.json(
      { error: "auth_callback_invalid_request", message: "code y state requeridos" },
      { status: 400 },
    );
  }
  
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0] ?? "unknown";
  const userAgent = request.headers.get("user-agent") ?? "unknown";
  
  try {
    const result = await handleAuthCallback(
      { code, state, ip, userAgent },
      {
        env: process.env as any,
        db: { upsertUser: db.upsertUser, createSession: db.createSession },
        log: logger,
        encrypt: encryptToken,
      },
    );
    
    const response = NextResponse.redirect(new URL(result.redirectTo, request.url));
    response.cookies.set("monstruo_session", result.cookieValue, {
      httpOnly: true,
      secure: true,
      sameSite: "lax",
      expires: result.cookieExpiresAt,
      path: "/",
    });
    
    return response;
  } catch (err: any) {
    logger.error("auth_callback_handler_error", { error: err.message });
    return NextResponse.redirect(
      new URL("/login?error=auth_callback_failed", request.url),
    );
  }
}
```

---

## `app/(protected)/layout.tsx` (server component)

```typescript
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { authenticate } from "@/lib/auth/middleware";
import { authDeps } from "@/lib/auth/deps";

export default async function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const session = cookieStore.get("monstruo_session")?.value;
  
  try {
    const user = await authenticate(session, authDeps);
    return (
      <UserContextProvider user={user}>
        {children}
      </UserContextProvider>
    );
  } catch (err: any) {
    if (err.code === "auth_user_suspended") {
      redirect("/suspended");
    }
    redirect("/login");
  }
}
```

---

## `app/(auth)/login/page.tsx`

```typescript
import { SignInWithManusButton } from "@monstruo/auth-ui";
// O importar directamente del template si no hay package compartido aún

export default function LoginPage({ searchParams }: { searchParams: { return_to?: string } }) {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div style={{ textAlign: "center", maxWidth: "400px" }}>
        <h1>Comando Central</h1>
        <p>Forja, vigila, decide. Inicia sesión para entrar.</p>
        <SignInWithManusButton
          returnTo={searchParams.return_to ?? "/dashboard"}
          variant="filled"
          size="lg"
        />
      </div>
    </main>
  );
}
```

---

## Tests E2E (Playwright)

```typescript
import { test, expect } from "@playwright/test";

test("login flow happy path", async ({ page, context }) => {
  await page.goto("/dashboard"); // protected
  await expect(page).toHaveURL(/\/login/);
  
  // Mock del provider (en CI usamos un Manus-Oauth mock server)
  await page.click('button[aria-label="Sign in with Manus"]');
  await page.waitForURL(/oauth\.manus\.im\/authorize/);
  
  // Mock acepta automáticamente
  await page.waitForURL(/\/dashboard/);
  
  const cookies = await context.cookies();
  const session = cookies.find(c => c.name === "monstruo_session");
  expect(session).toBeDefined();
  expect(session?.httpOnly).toBe(true);
  expect(session?.secure).toBe(true);
});
```

---

## Referencias

- Spec del Command Center: `docs/COMMAND_CENTER_SPEC.md` (cuando exista)
- DSC-X-003 — restricción dura
- `templates/` — base de los archivos
- Adaptación específica del Command Center: `apps/command-center/lib/auth/`

— Hilo Catastro, Sprint Catastro-B 2026-05-06
