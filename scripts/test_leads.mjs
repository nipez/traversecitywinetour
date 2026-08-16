import { parseLeadBody } from "../functions/_shared/leads.js";
import assert from "node:assert/strict";

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

console.log("lead validation tests passed");
