export const LEAD_TYPES = new Set([
  "newsletter",
  "lodging",
  "bach_kit",
  "advertise",
  "contact",
  "tour",
]);

export const PAYLOAD_FIELDS = {
  newsletter: [],
  lodging: ["property_name", "website", "property_type", "location", "tier", "notes"],
  bach_kit: ["bride_name", "weekend", "group_size", "vibe"],
  advertise: ["company", "budget", "message"],
  contact: ["subject", "message"],
  tour: ["party_size", "preferred_date", "message"],
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MAX_BODY = 12_288;
const MAX_EMAIL = 254;
const MAX_NAME = 120;
const MAX_FIELD = 500;
const MAX_NOTES = 2_000;
const MAX_SOURCE = 500;

export function jsonResponse(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...extraHeaders,
    },
  });
}

export function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const encoder = new TextEncoder();
  const left = encoder.encode(a);
  const right = encoder.encode(b);
  const len = Math.max(left.length, right.length);
  let diff = left.length === right.length ? 0 : 1;
  for (let i = 0; i < len; i += 1) {
    diff |= (left[i] || 0) ^ (right[i] || 0);
  }
  return diff === 0;
}

export function isAllowedOrigin(request) {
  const origin = request.headers.get("Origin");
  if (!origin) return true;
  const { origin: requestOrigin } = new URL(request.url);
  if (origin === requestOrigin) return true;
  try {
    const parsed = new URL(origin);
    return parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1";
  } catch {
    return false;
  }
}

export function clientIp(request) {
  return (
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("True-Client-IP") ||
    request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim() ||
    "unknown"
  );
}

export async function hashIp(ip) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(ip));
  return [...new Uint8Array(bytes)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .slice(0, 32);
}

function cleanText(value, max) {
  if (value == null) return "";
  return String(value).replace(/\s+/g, " ").trim().slice(0, max);
}

export function parseLeadBody(text) {
  if (text.length > MAX_BODY) {
    return { error: "Payload too large", status: 413 };
  }

  let raw;
  try {
    raw = JSON.parse(text);
  } catch {
    return { error: "Invalid JSON", status: 400 };
  }
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return { error: "Invalid JSON", status: 400 };
  }

  // Honeypot: treat as success without storing. Do not use "website" —
  // the lodging form collects a real booking URL under that name.
  if (cleanText(raw.hp, 80) || cleanText(raw.company_url, 80)) {
    return { honeypot: true };
  }

  const type = cleanText(raw.type, 40);
  if (!LEAD_TYPES.has(type)) {
    return { error: "Unknown lead type", status: 400 };
  }

  const email = cleanText(raw.email, MAX_EMAIL).toLowerCase();
  if (!email || !EMAIL_RE.test(email)) {
    return { error: "A valid email is required", status: 400 };
  }

  if (raw.consent !== true && raw.consent !== "true" && raw.consent !== "on") {
    return { error: "Consent is required", status: 400 };
  }

  const name = cleanText(raw.name, MAX_NAME);
  if ((type === "lodging" || type === "bach_kit" || type === "contact" || type === "tour") && !name) {
    return { error: "Name is required", status: 400 };
  }

  const payloadIn = raw.payload && typeof raw.payload === "object" && !Array.isArray(raw.payload)
    ? raw.payload
    : raw;
  const payload = {};
  for (const field of PAYLOAD_FIELDS[type] || []) {
    const max = field === "notes" || field === "message" ? MAX_NOTES : MAX_FIELD;
    const value = cleanText(payloadIn[field] ?? raw[field], max);
    if (value) payload[field] = value;
  }

  if (type === "lodging" && !payload.property_name) {
    return { error: "Property name is required", status: 400 };
  }

  return {
    lead: {
      type,
      email,
      name: name || null,
      payload,
      source_page: cleanText(raw.source_page, MAX_SOURCE) || null,
      utm_source: cleanText(raw.utm_source, 80) || null,
      utm_medium: cleanText(raw.utm_medium, 80) || null,
      utm_campaign: cleanText(raw.utm_campaign, 80) || null,
    },
  };
}

export async function enforceRateLimit(db, ipHash, type) {
  const hourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
  const { count } = await db
    .prepare("SELECT COUNT(*) AS count FROM leads WHERE ip_hash = ? AND created_at >= ?")
    .bind(ipHash, hourAgo)
    .first();

  const limit = type === "newsletter" ? 8 : 12;
  if ((count || 0) >= limit) {
    return { error: "Too many submissions. Please try again later.", status: 429 };
  }
  return { ok: true };
}
