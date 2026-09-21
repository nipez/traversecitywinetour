/**
 * Best-effort operator alert for new leads.
 * Prefer Resend email; fall back to webhook. Never throws to callers.
 */

const DEFAULT_TO = "nickperez@gmail.com";
const DEFAULT_FROM = "Traverse City Wine Tour <onboarding@resend.dev>";

const TYPE_LABELS = {
  newsletter: "Newsletter signup",
  lodging: "Lodging listing request",
  bach_kit: "Bachelorette planning kit",
  advertise: "Advertise inquiry",
  contact: "Contact message",
  tour: "Tour inquiry",
};

/**
 * @param {object} env
 * @param {{ kind?: string, subject: string, text: string, html?: string }} payload
 * @returns {Promise<{ emailed: boolean, webhooked: boolean, status: string }>}
 */
export async function notifyOperator(env, payload) {
  const to = (env.NOTIFY_EMAIL || "").trim() || DEFAULT_TO;
  const from = (env.NOTIFY_FROM_EMAIL || "").trim() || DEFAULT_FROM;
  const kind = payload.kind || "lead";

  let emailed = false;
  let webhooked = false;
  let status = "skipped";

  if (env.RESEND_API_KEY) {
    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from,
          to: [to],
          subject: payload.subject,
          text: payload.text,
          html: payload.html ?? `<pre>${escapeHtml(payload.text)}</pre>`,
        }),
      });
      if (!res.ok) {
        const body = await res.text();
        console.error("Resend notify failed", res.status, body);
        status = "email_failed";
      } else {
        emailed = true;
        status = "emailed";
      }
    } catch (err) {
      console.error("Resend notify error", err);
      status = "email_failed";
    }
  }

  if (env.NOTIFY_WEBHOOK_URL) {
    try {
      const res = await fetch(env.NOTIFY_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          kind,
          subject: payload.subject,
          text: payload.text,
          emailed,
          to,
        }),
      });
      if (!res.ok) {
        console.error("Webhook notify failed", res.status, await res.text());
        if (!emailed) status = "webhook_failed";
      } else {
        webhooked = true;
        if (!emailed) status = "webhooked";
        else status = "emailed";
      }
    } catch (err) {
      console.error("Webhook notify error", err);
      if (!emailed) status = "webhook_failed";
    }
  }

  if (!env.RESEND_API_KEY && !env.NOTIFY_WEBHOOK_URL) {
    console.warn(
      "notifyOperator: no RESEND_API_KEY or NOTIFY_WEBHOOK_URL configured",
      payload.subject
    );
    status = "unconfigured";
  }

  console.log("notifyOperator", {
    kind,
    subject: payload.subject,
    emailed,
    webhooked,
    status,
    hasWebhook: Boolean(env.NOTIFY_WEBHOOK_URL),
  });

  return { emailed, webhooked, status };
}

/**
 * Build subject/text for a newly inserted lead.
 * @param {object} lead
 * @param {string} [adminUrl]
 */
export function formatLeadNotify(lead, adminUrl) {
  const label = TYPE_LABELS[lead.type] || lead.type;
  const payload = lead.payload && typeof lead.payload === "object" ? lead.payload : {};
  const payloadLines = Object.entries(payload)
    .filter(([, v]) => v != null && String(v).trim() !== "")
    .map(([k, v]) => `${k}: ${v}`);

  const lines = [
    `New ${label}`,
    "",
    `ID: ${lead.id}`,
    `Type: ${lead.type}`,
    `Email: ${lead.email}`,
    lead.name ? `Name: ${lead.name}` : null,
    lead.source_page ? `Source page: ${lead.source_page}` : null,
    lead.utm_source ? `utm_source: ${lead.utm_source}` : null,
    lead.utm_medium ? `utm_medium: ${lead.utm_medium}` : null,
    lead.utm_campaign ? `utm_campaign: ${lead.utm_campaign}` : null,
    payloadLines.length ? "" : null,
    payloadLines.length ? "Details:" : null,
    ...payloadLines,
    "",
    adminUrl ? `Review: ${adminUrl}` : "Review: /admin/leads",
  ].filter((line) => line != null);

  return {
    kind: "lead",
    subject: `${label}: ${lead.email}`,
    text: lines.join("\n"),
  };
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
