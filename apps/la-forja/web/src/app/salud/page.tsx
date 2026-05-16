import { buildForjaApi, ForjaApiError } from "@/lib/api";

/**
 * La Forja — diagnóstico de estado.
 * Sprint LA-FORJA-001 D3.0.
 *
 * Pega un GET /health al backend Hono y muestra el resultado binario.
 * Server Component: la llamada se hace en el servidor de Next, no expone
 * el backend al cliente directamente.
 */
async function fetchSalud() {
  const api = buildForjaApi();
  try {
    const resp = await api.health();
    return { ok: true as const, data: resp };
  } catch (err) {
    if (err instanceof ForjaApiError) {
      return {
        ok: false as const,
        status: err.status,
        requestId: err.requestId,
        body: err.body,
      };
    }
    return {
      ok: false as const,
      status: 0,
      requestId: "n/a",
      body: err instanceof Error ? err.message : String(err),
    };
  }
}

export default async function SaludPage() {
  const result = await fetchSalud();

  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col gap-10 px-6 py-16">
      <header className="flex items-baseline gap-3">
        <span className="text-forja-500 font-mono text-xs tracking-[0.3em] uppercase">
          La Forja · estado
        </span>
      </header>

      <h1 className="text-graphite-100 text-3xl font-semibold tracking-tight">
        Diagnóstico binario del backend.
      </h1>

      {result.ok ? (
        <section className="border-forja-500/40 bg-graphite-900 flex flex-col gap-3 border p-6 font-mono text-sm">
          <div className="text-forja-500">[la-forja:health_ok]</div>
          <div className="text-graphite-100">status: {result.data.status}</div>
          <div className="text-acero-500">service: {result.data.service}</div>
          <div className="text-acero-500">version: {result.data.version}</div>
          <div className="text-acero-500">timestamp: {result.data.timestamp}</div>
        </section>
      ) : (
        <section className="border-forja-700 bg-graphite-900 flex flex-col gap-3 border p-6 font-mono text-sm">
          <div className="text-forja-500">
            [la-forja:web_health_check_failed]
          </div>
          <div className="text-graphite-100">status: {result.status}</div>
          <div className="text-acero-500">request_id: {result.requestId}</div>
          <pre className="text-acero-500 max-w-full overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(result.body, null, 2)}
          </pre>
        </section>
      )}
    </main>
  );
}
