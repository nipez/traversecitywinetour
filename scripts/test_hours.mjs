/**
 * Unit tests for js/hours.js — run via `node scripts/test_hours.mjs`
 * Also included from npm test.
 */
import { createRequire } from "module";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import vm from "vm";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

function loadHours() {
  const code = readFileSync(join(root, "js/hours.js"), "utf8");
  const dataCode = readFileSync(join(root, "js/venue-hours-data.js"), "utf8");
  const sandbox = { window: {}, globalThis: {} };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.runInNewContext(dataCode + "\n" + code, sandbox);
  return sandbox.window.TCWT_HOURS || sandbox.TCWT_HOURS;
}

const H = loadHours();
let failed = 0;

function assert(cond, msg) {
  if (!cond) {
    failed++;
    console.error("FAIL:", msg);
  }
}

function assertEq(a, b, msg) {
  if (a !== b) {
    failed++;
    console.error("FAIL:", msg, "| got", a, "expected", b);
  }
}

// Daily
{
  const p = H.parseHours("Daily 10am–6pm");
  assert(p.ok, "daily ok");
  assertEq(H.dayStatus(p, 0), "open", "daily sun open");
  assertEq(H.dayStatus(p, 3), "open", "daily wed open");
  assertEq(H.dayHoursLabel(p, 1), "10am–6pm", "daily label");
}

// Mon–Sat + Sun
{
  const p = H.parseHours("Mon–Sat 10am–6pm · Sun 12–5pm");
  assert(p.ok, "mon-sat/sun ok");
  assertEq(H.dayStatus(p, 0), "open", "sun open");
  assertEq(H.dayHoursLabel(p, 0), "12pm–5pm", "sun hours");
  assertEq(H.dayHoursLabel(p, 1), "10am–6pm", "mon hours");
  assertEq(H.dayStatus(p, 6), "open", "sat open");
}

// Wraparound Thu–Mon
{
  const p = H.parseHours("Thu–Mon 12–5pm (Seasonal)");
  assert(p.ok, "thu-mon ok");
  assert(p.seasonal, "seasonal flag");
  assertEq(H.dayStatus(p, 4), "open", "thu open");
  assertEq(H.dayStatus(p, 0), "open", "sun open");
  assertEq(H.dayStatus(p, 1), "open", "mon open");
  assertEq(H.dayStatus(p, 2), "closed", "tue closed");
  assertEq(H.dayStatus(p, 3), "closed", "wed closed");
}

// Fri–Sat overnight-ish brewery hours
{
  const p = H.parseHours("Mon–Thu 3–11pm · Fri 12–12am · Sat 11am–12am · Sun 11am–10pm");
  assert(p.ok, "brewery ok");
  assertEq(H.dayStatus(p, 5), "open", "fri open");
  assertEq(H.dayHoursLabel(p, 1), "3pm–11pm", "mon brewery");
}

// Sun–Thu range
{
  const p = H.parseHours("Sun–Thu 11:30am–10pm · Fri–Sat 11:30am–11pm");
  assert(p.ok, "sun-thu ok");
  assertEq(H.dayHoursLabel(p, 0), "11:30am–10pm", "sun");
  assertEq(H.dayHoursLabel(p, 5), "11:30am–11pm", "fri");
}

// Empty / missing
{
  const p = H.parseHours("");
  assert(!p.ok, "empty not ok");
  assertEq(H.dayStatus(p, 1), "unknown", "empty unknown");
}

// Unparseable garbage
{
  const p = H.parseHours("by appointment only");
  assert(!p.ok, "appointment not ok");
}

// Schema
{
  const p = H.parseHours("Mon–Sat 10am–6pm · Sun 12–5pm");
  const spec = H.toOpeningHoursSpecification(p);
  assert(spec && spec.length >= 2, "schema specs");
  assert(
    spec.some((s) => s.opens === "10:00" && s.closes === "18:00"),
    "schema mon-sat times"
  );
}

// Seasonal schedule pick (winter)
{
  const venue = {
    hoursStatus: "verified",
    hoursCheckedAt: "2026-11-25",
    hours: "Daily 11am–5pm",
    hoursSchedules: [
      {
        id: "winter",
        validFrom: "11-01",
        validThrough: "04-30",
        hours: "Daily 11am–5pm",
      },
      {
        id: "summer",
        validFrom: "05-01",
        validThrough: "10-31",
        hours: "Daily 11am–6pm",
      },
    ],
    holidayClosures: [],
  };
  const carrier = H.detroitNow();
  // Force November-like carrier fields
  carrier._y = 2026;
  carrier._mo = 10; // November
  carrier._d = 25;
  const resolved = H.resolveVenueHours(venue, carrier);
  assert(resolved.ok, "winter resolve ok");
  assertEq(resolved.displayHours, "Daily 11am–5pm", "winter hours picked");
  assertEq(H.dayStatus(resolved, 1), "open", "winter mon open");
  const spec = H.toOpeningHoursSpecification(resolved);
  assert(spec && spec[0].validFrom, "schema has validFrom");
  assert(spec[0].validThrough, "schema has validThrough");
}

// Call-ahead never shows open
{
  const venue = {
    hoursStatus: "call-ahead",
    hours: "Fri–Sat 12–5pm",
    hoursSchedules: [],
  };
  const resolved = H.resolveVenueHours(venue);
  assertEq(H.dayStatus(resolved, 5), "unknown", "call-ahead fri unknown");
  assertEq(H.toOpeningHoursSpecification(resolved), null, "no schema for call-ahead");
}

// Closed season
{
  const venue = {
    hoursStatus: "closed-season",
    hours: "Closed for the season",
    hoursSchedules: [
      {
        id: "summer",
        validFrom: "06-13",
        validThrough: "10-20",
        hours: "Sat 12–5pm",
      },
    ],
  };
  const carrier = H.detroitNow();
  carrier._y = 2026;
  carrier._mo = 10;
  carrier._d = 25;
  const resolved = H.resolveVenueHours(venue, carrier);
  assertEq(H.dayStatus(resolved, 6), "closed", "closed-season sat closed");
  assertEq(H.toOpeningHoursSpecification(resolved), null, "no schema closed-season");
}

// Month-day range wrap
{
  assert(H.monthDayInRange("11-25", "11-01", "04-30"), "nov in winter wrap");
  assert(H.monthDayInRange("02-10", "11-01", "04-30"), "feb in winter wrap");
  assert(!H.monthDayInRange("06-15", "11-01", "04-30"), "jun not in winter wrap");
}

// Coverage against repo data — every venue must be verified, call-ahead, or closed-season
{
  const require = createRequire(import.meta.url);
  const wineryData = require(join(root, "data-wineries.json"));
  const cideries = require(join(root, "data-cideries.json"));
  const breweries = require(join(root, "data-breweries.json"));
  const sets = [
    ["wineries", wineryData.wineries],
    ["cideries", cideries],
    ["breweries", breweries],
  ];
  let verified = 0;
  let callAhead = 0;
  let closedSeason = 0;
  const bad = [];
  for (const [label, items] of sets) {
    for (const v of items) {
      const status = v.hoursStatus;
      if (!["verified", "call-ahead", "closed-season"].includes(status)) {
        bad.push([label, v.name, "missing hoursStatus"]);
        continue;
      }
      if (!v.hoursCheckedAt) bad.push([label, v.name, "missing hoursCheckedAt"]);
      if (status === "verified") {
        verified++;
        const resolved = H.resolveVenueHours(v);
        // For today's date: either parseable schedule, holiday closed, or call-ahead fallback
        if (
          resolved.hoursStatus === "verified" &&
          resolved.ok === false &&
          !resolved.holidayClosed
        ) {
          // verified but no covering schedule today → treated as call-ahead internally
        }
        if (resolved.ok && resolved.byDay.some(Boolean)) {
          const spec = H.toOpeningHoursSpecification(resolved);
          assert(spec && spec.length, `schema for ${v.name}`);
        }
      } else if (status === "call-ahead") {
        callAhead++;
        const resolved = H.resolveVenueHours(v);
        assertEq(
          H.toOpeningHoursSpecification(resolved),
          null,
          `no schema call-ahead ${v.name}`
        );
      } else {
        closedSeason++;
      }
    }
  }
  console.log(
    `Status: ${verified} verified / ${callAhead} call-ahead / ${closedSeason} closed-season`
  );
  if (bad.length) {
    console.log("Bad venues:");
    bad.forEach((b) => console.log(" -", b.join(" | ")));
  }
  assert(bad.length === 0, "all venues have status + checkedAt");
  assert(verified + callAhead + closedSeason === 34 + 6 + 15, "expected venue counts");
}

// formatCheckedNote
{
  assertEq(
    H.formatCheckedNote("2026-11-25"),
    "Hours last checked Nov 25, 2026",
    "checked note format"
  );
}

if (failed) {
  console.error(`\n${failed} assertion(s) failed`);
  process.exit(1);
}
console.log("hours tests passed");
