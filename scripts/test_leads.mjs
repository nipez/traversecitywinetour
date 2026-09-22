import assert from "node:assert/strict";
import { parseLeadBody } from "../functions/_shared/leads.js";
import {
  escapeHtml,
  formatLeadNotify,
  notifyOperator,
} from "../functions/_shared/notify.js";

function expectError(body, message) {
  const result = parseLeadBody(JSON.stringify(body));
  assert.equal(result.error, message, JSON.stringify(result));
}

expectError({}, "Unknown lead type");
expectError({ type: "newsletter", email: "not-an-email", consent: true }, "A valid email is required");
expectError({ type: "newsletter", email: "a@b.com" }, "Consent is required");
expectError({ type: "lodging", email: "a@b.com", consent: true, name: "Jane" }, "Property name is required");

const honey = parseLeadBody(JSON.stringify({
  type: "newsletter",
  email: "bot@example.com",
  consent: true,
  hp: "https://spam.test",
}));
assert.equal(honey.honeypot, true);

const ok = parseLeadBody(JSON.stringify({
  type: "bach_kit",
  email: "moh@example.com",
  name: "Alex",
  consent: true,
  bride_name: "Sam",
  weekend: "September 2026",
  extra: "ignore me",
}));
assert.equal(ok.lead.type, "bach_kit");
assert.equal(ok.lead.email, "moh@example.com");
assert.equal(ok.lead.payload.bride_name, "Sam");
assert.equal(ok.lead.payload.extra, undefined);

const lodging = parseLeadBody(JSON.stringify({
  type: "lodging",
  email: "host@example.com",
  name: "Jane",
  consent: "on",
  property_name: "Bay Inn",
  notes: "  lake view  ",
}));
assert.equal(lodging.lead.payload.property_name, "Bay Inn");
assert.equal(lodging.lead.payload.notes, "lake view");

const tour = parseLeadBody(JSON.stringify({
  type: "tour",
  email: "guest@example.com",
  name: "Riley",
  consent: true,
  operator: "Grand Traverse Limo",
  party_size: "8",
  preferred_date: "2026-09-12",
  message: "Hotel pickup at Park Place",
}));
assert.equal(tour.lead.type, "tour");
assert.equal(tour.lead.payload.operator, "Grand Traverse Limo");
assert.equal(tour.lead.payload.party_size, "8");

expectError({ type: "tour", email: "a@b.com", consent: true }, "Name is required");

expectError({ type: "advertise", email: "a@b.com", consent: true }, "Name is required");

const advertise = parseLeadBody(JSON.stringify({
  type: "advertise",
  email: "ops@winery.example",
  name: "Jordan Lee",
  consent: true,
  payload: {
    company: "Bayview Cellars",
    budget: "Sponsored Profile (~$150/month)",
    message: "Interested in Old Mission placement for harvest season.",
  },
}));
assert.equal(advertise.lead.type, "advertise");
assert.equal(advertise.lead.name, "Jordan Lee");
assert.equal(advertise.lead.payload.company, "Bayview Cellars");
assert.equal(advertise.lead.payload.budget, "Sponsored Profile (~$150/month)");
assert.equal(advertise.lead.payload.message, "Interested in Old Mission placement for harvest season.");

// --- notify formatting ---
const notify = formatLeadNotify(
  {
    id: "lead-123",
    type: "bach_kit",
    email: "moh@example.com",
    name: "Alex",
    source_page: "/bachelorette.html",
    utm_source: "ig",
    utm_medium: "social",
    utm_campaign: "bach2026",
    payload: { bride_name: "Sam", weekend: "September 2026" },
  },
  "https://traversecitywinetour.com/admin/leads"
);
assert.equal(notify.kind, "lead");
assert.match(notify.subject, /Bachelorette planning kit/);
assert.match(notify.subject, /moh@example.com/);
assert.match(notify.text, /ID: lead-123/);
assert.match(notify.text, /bride_name: Sam/);
assert.match(notify.text, /utm_source: ig/);
assert.match(notify.text, /https:\/\/traversecitywinetour.com\/admin\/leads/);

assert.equal(escapeHtml("<script>"), "&lt;script&gt;");

// --- notifyOperator: unconfigured (no throw) ---
{
  const result = await notifyOperator({}, { subject: "test", text: "hello" });
  assert.equal(result.status, "unconfigured");
  assert.equal(result.emailed, false);
}

// --- notifyOperator: Resend success path (mocked fetch) ---
{
  const originalFetch = globalThis.fetch;
  let called = null;
  globalThis.fetch = async (url, init) => {
    called = { url, init };
    return new Response(JSON.stringify({ id: "re_test" }), { status: 200 });
  };
  try {
    const result = await notifyOperator(
      {
        RESEND_API_KEY: "re_test_key",
        NOTIFY_EMAIL: "ops@example.com",
        NOTIFY_FROM_EMAIL: "TCWT <onboarding@resend.dev>",
      },
      { kind: "lead", subject: "Lead: test", text: "body" }
    );
    assert.equal(result.emailed, true);
    assert.equal(result.status, "emailed");
    assert.equal(called.url, "https://api.resend.com/emails");
    const body = JSON.parse(called.init.body);
    assert.deepEqual(body.to, ["ops@example.com"]);
    assert.equal(body.from, "TCWT <onboarding@resend.dev>");
    assert.equal(body.subject, "Lead: test");
  } finally {
    globalThis.fetch = originalFetch;
  }
}

// --- notifyOperator: Resend fail + webhook success ---
{
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    if (String(url).includes("resend.com")) {
      return new Response("nope", { status: 500 });
    }
    return new Response("ok", { status: 200 });
  };
  try {
    const result = await notifyOperator(
      {
        RESEND_API_KEY: "re_bad",
        NOTIFY_WEBHOOK_URL: "https://hooks.example.com/lead",
      },
      { subject: "Lead: webhook", text: "body" }
    );
    assert.equal(result.emailed, false);
    assert.equal(result.webhooked, true);
    assert.equal(result.status, "webhooked");
  } finally {
    globalThis.fetch = originalFetch;
  }
}

console.log("lead validation + notify tests passed");
