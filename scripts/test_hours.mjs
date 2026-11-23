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
  const sandbox = { window: {}, globalThis: {} };
  sandbox.globalThis = sandbox;
  vm.runInNewContext(code, sandbox);
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

// Coverage against repo data
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
  let usable = 0;
  let missing = 0;
  const bad = [];
  for (const [label, items] of sets) {
    for (const v of items) {
      const p = H.parseHours(v.hours);
      if (p.ok) usable++;
      else {
        missing++;
        bad.push([label, v.name, v.hours]);
      }
    }
  }
  console.log(
    `Coverage: ${usable} usable / ${usable + missing} total; ${missing} missing/unparseable`
  );
  if (bad.length) {
    console.log("Unparseable:");
    bad.forEach((b) => console.log(" -", b.join(" | ")));
  }
  assert(usable + missing === 35 + 6 + 15, "expected venue counts");
}

if (failed) {
  console.error(`\n${failed} assertion(s) failed`);
  process.exit(1);
}
console.log("hours tests passed");
