import { isAllowedOrigin, jsonResponse, timingSafeEqual } from "../../_shared/leads.js";

const ALLOWED_TYPES = new Set([
  "newsletter",
  "lodging",
  "bach_kit",
  "advertise",
  "contact",
  "tour",
]);

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!isAllowedOrigin(request)) {
    return jsonResponse({ error: "Forbidden" }, 403);
  }
  if (!authorize(request, env)) {
    return jsonResponse({ error: "Unauthorized" }, 401, corsHeaders(request));
  }
  if (!env.DB) {
    return jsonResponse({ error: "Lead storage is not configured" }, 503, corsHeaders(request));
  }

  const url = new URL(request.url);
  const type = (url.searchParams.get("type") || "").trim();
  const limit = clampInt(url.searchParams.get("limit"), 50, 1, 200);
  const offset = clampInt(url.searchParams.get("offset"), 0, 0, 10_000);

  const conditions = [];
  const binds = [];
  if (type && ALLOWED_TYPES.has(type)) {
    conditions.push("type = ?");
    binds.push(type);
  }
  const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";

  const [countRow, rows] = await env.DB.batch([
    env.DB.prepare(`SELECT COUNT(*) AS total FROM leads ${where}`).bind(...binds),
    env.DB.prepare(
      `SELECT id, type, email, name, payload, source_page, utm_source, utm_medium,
              utm_campaign, created_at, status, notes
       FROM leads ${where}
       ORDER BY created_at DESC
       LIMIT ? OFFSET ?`
    ).bind(...binds, limit, offset),
  ]);

  const leads = (rows.results || []).map((row) => ({
    ...row,
    payload: safeJson(row.payload),
  }));

  return jsonResponse(
    {
      ok: true,
      total: countRow.results?.[0]?.total || 0,
      limit,
      offset,
      leads,
    },
    200,
    corsHeaders(request)
  );
}

export async function onRequestOptions(context) {
  if (!isAllowedOrigin(context.request)) {
    return jsonResponse({ error: "Forbidden" }, 403);
  }
  return new Response(null, { status: 204, headers: corsHeaders(context.request) });
}

function authorize(request, env) {
  const expected = env.ADMIN_TOKEN;
  if (!expected) return false;
  const header = request.headers.get("Authorization") || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : header;
  return timingSafeEqual(token, expected);
}

function clampInt(value, fallback, min, max) {
  const n = Number.parseInt(value, 10);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, n));
}

function safeJson(value) {
  if (!value) return {};
  try {
    return JSON.parse(value);
  } catch {
    return {};
  }
}

function corsHeaders(request) {
  const origin = request.headers.get("Origin");
  const headers = {
    "access-control-allow-methods": "GET, OPTIONS",
    "access-control-allow-headers": "content-type, authorization",
    vary: "Origin",
  };
  if (origin && isAllowedOrigin(request)) {
    headers["access-control-allow-origin"] = origin;
  }
  return headers;
}
