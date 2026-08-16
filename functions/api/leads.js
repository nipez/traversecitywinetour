import {
  enforceRateLimit,
  hashIp,
  isAllowedOrigin,
  jsonResponse,
  parseLeadBody,
  clientIp,
} from "../_shared/leads.js";

export async function onRequestOptions(context) {
  if (!isAllowedOrigin(context.request)) {
    return jsonResponse({ error: "Forbidden" }, 403);
  }
  return new Response(null, {
    status: 204,
    headers: corsHeaders(context.request),
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!isAllowedOrigin(request)) {
    return jsonResponse({ error: "Forbidden" }, 403);
  }
  if (!env.DB) {
    return jsonResponse({ error: "Lead storage is not configured" }, 503, corsHeaders(request));
  }

  const contentLength = Number(request.headers.get("content-length") || "0");
  if (contentLength > 12_288) {
    return jsonResponse({ error: "Payload too large" }, 413, corsHeaders(request));
  }

  const parsed = parseLeadBody(await request.text());
  if (parsed.honeypot) {
    return jsonResponse({ ok: true }, 200, corsHeaders(request));
  }
  if (parsed.error) {
    return jsonResponse({ error: parsed.error }, parsed.status, corsHeaders(request));
  }

  const ipHash = await hashIp(clientIp(request));
  const limited = await enforceRateLimit(env.DB, ipHash, parsed.lead.type);
  if (limited.error) {
    return jsonResponse({ error: limited.error }, limited.status, corsHeaders(request));
  }

  const id = crypto.randomUUID();
  const lead = parsed.lead;

  try {
    await env.DB.prepare(
      `INSERT INTO leads (
        id, type, email, name, payload, source_page,
        utm_source, utm_medium, utm_campaign, ip_hash, status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')`
    )
      .bind(
        id,
        lead.type,
        lead.email,
        lead.name,
        JSON.stringify(lead.payload),
        lead.source_page,
        lead.utm_source,
        lead.utm_medium,
        lead.utm_campaign,
        ipHash
      )
      .run();
  } catch (error) {
    const message = String(error?.message || error);
    if (lead.type === "newsletter" && /UNIQUE|constraint/i.test(message)) {
      return jsonResponse({ ok: true, already_subscribed: true }, 200, corsHeaders(request));
    }
    console.error("lead insert failed", message);
    return jsonResponse({ error: "Could not save your request" }, 500, corsHeaders(request));
  }

  return jsonResponse({ ok: true, id }, 201, corsHeaders(request));
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  if (context.request.method === "OPTIONS") return onRequestOptions(context);
  return jsonResponse({ error: "Method not allowed" }, 405, corsHeaders(context.request));
}

function corsHeaders(request) {
  const origin = request.headers.get("Origin");
  const headers = {
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    vary: "Origin",
  };
  if (origin && isAllowedOrigin(request)) {
    headers["access-control-allow-origin"] = origin;
  }
  return headers;
}
