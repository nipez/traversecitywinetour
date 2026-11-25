/**
 * Conservative free-text hours parser for Traverse City Wine Tour venue listings.
 * Source strings come from data-*.json only — never invent schedules.
 *
 * Supports seasonal schedules (validFrom/validThrough MM-DD), holiday closures,
 * and verified / call-ahead / closed-season status.
 *
 * Supported patterns (en dash / hyphen / middle-dot separators):
 *   Daily 10am–6pm
 *   Mon–Sat 10am–6pm · Sun 12–5pm
 *   Thu–Mon 12–5pm
 *   Sun–Thu 11:30am–10pm · Fri–Sat 11:30am–11pm
 *   Mon 12–8pm · Tue–Sat 12–10pm · Sun 12–9pm
 * Parenthetical notes like (seasonal) are kept as notes, not schedule data.
 */
(function (global) {
  var DAY_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  var DAY_SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var DAY_ALIASES = {
    sun: 0,
    sunday: 0,
    mon: 1,
    monday: 1,
    tue: 2,
    tues: 2,
    tuesday: 2,
    wed: 3,
    wednesday: 3,
    thu: 4,
    thur: 4,
    thurs: 4,
    thursday: 4,
    fri: 5,
    friday: 5,
    sat: 6,
    saturday: 6,
  };

  var MISSING_LABEL = "Hours not listed — check with the winery";
  var CALL_AHEAD_LABEL = "Call ahead — hours not verified for this season";
  var CLOSED_SEASON_LABEL = "Closed for the season";
  var SEASONAL_NOTE =
    "Hours change seasonally — call ahead to confirm before you go.";

  function normalize(raw) {
    if (raw == null) return "";
    return String(raw)
      .replace(/\u2013|\u2014|\u2212/g, "-")
      .replace(/\u00b7|\u2022|\|/g, "·")
      .replace(/\s+/g, " ")
      .trim();
  }

  function parseTimeToken(token) {
    var t = String(token).trim().toLowerCase().replace(/\s+/g, "");
    var m = t.match(/^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$/);
    if (!m) return null;
    var hour = parseInt(m[1], 10);
    var minute = m[2] ? parseInt(m[2], 10) : 0;
    var mer = m[3] || null;
    if (hour > 24 || minute > 59) return null;
    if (mer) {
      if (hour < 1 || hour > 12) return null;
      if (mer === "am") {
        if (hour === 12) hour = 0;
      } else if (hour !== 12) {
        hour += 12;
      }
    } else {
      if (hour > 23) return null;
    }
    return { hour: hour, minute: minute, mer: mer, raw: token };
  }

  function applyMeridiem(left, right) {
    if (left.mer || !right.mer) return left;
    var hour = left.hour;
    var mer = right.mer;
    if (mer === "am") {
      if (hour === 12) hour = 0;
      else if (hour > 12) return null;
    } else {
      if (hour !== 12 && hour < 12) hour += 12;
    }
    return { hour: hour, minute: left.minute, mer: mer, raw: left.raw };
  }

  function toMinutes(t) {
    return t.hour * 60 + t.minute;
  }

  function formatTime(t) {
    var h = t.hour;
    var m = t.minute;
    var mer = h >= 12 ? "pm" : "am";
    var h12 = h % 12;
    if (h12 === 0) h12 = 12;
    return m ? h12 + ":" + String(m).padStart(2, "0") + mer : h12 + mer;
  }

  function formatTime24(t) {
    return (
      String(t.hour).padStart(2, "0") +
      ":" +
      String(t.minute).padStart(2, "0")
    );
  }

  function expandDayRange(startIdx, endIdx) {
    var days = [];
    var i = startIdx;
    for (var n = 0; n < 7; n++) {
      days.push(i);
      if (i === endIdx) break;
      i = (i + 1) % 7;
    }
    return days;
  }

  function parseDayToken(token) {
    var t = String(token).trim().toLowerCase();
    if (t === "daily" || t === "every day" || t === "everyday") {
      return { type: "daily" };
    }
    var range = t.match(/^([a-z]+)\s*-\s*([a-z]+)$/);
    if (range) {
      var a = DAY_ALIASES[range[1]];
      var b = DAY_ALIASES[range[2]];
      if (a == null || b == null) return null;
      return { type: "range", days: expandDayRange(a, b) };
    }
    var single = DAY_ALIASES[t];
    if (single != null) return { type: "single", days: [single] };
    return null;
  }

  function parseTimeRange(text) {
    var cleaned = text.trim();
    cleaned = cleaned.replace(/\([^)]*\)\s*$/g, "").trim();
    var m = cleaned.match(
      /^(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*-\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))$/i
    );
    if (!m) {
      m = cleaned.match(
        /^(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*-\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)$/i
      );
    }
    if (!m) return null;
    var right = parseTimeToken(m[2]);
    var left = parseTimeToken(m[1]);
    if (!left || !right) return null;
    if (!right.mer && !left.mer) return null;
    if (!right.mer && left.mer) return null;
    left = applyMeridiem(left, right);
    if (!left) return null;
    var openM = toMinutes(left);
    var closeM = toMinutes(right);
    if (closeM === 0 && /12\s*am/i.test(m[2])) closeM = 24 * 60;
    if (closeM <= openM) {
      if (closeM < openM && right.hour < 12 && right.mer === "am") {
        closeM += 24 * 60;
      } else {
        return null;
      }
    }
    return {
      opens: left,
      closes: {
        hour: Math.floor((closeM % (24 * 60)) / 60),
        minute: closeM % 60,
        mer: right.mer,
        raw: right.raw,
      },
      openMinutes: openM,
      closeMinutes: closeM,
      label: formatTime(left) + "–" + formatTime(right),
    };
  }

  /**
   * @returns {{
   *   ok: boolean,
   *   raw: string,
   *   seasonal: boolean,
   *   note: string|null,
   *   byDay: Array<null|{label:string,opens:object,closes:object,openMinutes:number,closeMinutes:number}>,
   *   missingLabel: string
   * }}
   */
  function parseHours(raw) {
    var original = raw == null ? "" : String(raw).trim();
    var result = {
      ok: false,
      raw: original,
      seasonal: false,
      note: null,
      byDay: [null, null, null, null, null, null, null],
      missingLabel: MISSING_LABEL,
    };
    if (!original) return result;

    var text = normalize(original);
    var notes = [];
    text = text.replace(/\(([^)]+)\)/g, function (_, inner) {
      notes.push(inner.trim());
      return " ";
    });
    text = text.replace(/\s+/g, " ").trim();
    result.seasonal = notes.some(function (n) {
      return /seasonal|vary|varies|appointment|call ahead/i.test(n);
    });
    if (notes.length) result.note = notes.join("; ");

    var segments = text
      .split("·")
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
    if (!segments.length) return result;

    var assigned = 0;
    for (var s = 0; s < segments.length; s++) {
      var seg = segments[s];
      var dm = seg.match(
        /^((?:daily|every\s*day|everyday|[A-Za-z]+(?:\s*-\s*[A-Za-z]+)?(?:\s*,\s*[A-Za-z]+(?:\s*-\s*[A-Za-z]+)?)*)\s+)(\d.+)$/i
      );
      if (!dm) return result;
      var dayPart = dm[1].trim();
      var timePart = dm[2].trim();
      var time = parseTimeRange(timePart);
      if (!time) return result;

      var dayChunks = dayPart.split(",").map(function (c) {
        return c.trim();
      });
      for (var c = 0; c < dayChunks.length; c++) {
        var days = parseDayToken(dayChunks[c]);
        if (!days) return result;
        var list =
          days.type === "daily" ? [0, 1, 2, 3, 4, 5, 6] : days.days;
        for (var d = 0; d < list.length; d++) {
          result.byDay[list[d]] = {
            label: time.label,
            opens: time.opens,
            closes: time.closes,
            openMinutes: time.openMinutes,
            closeMinutes: time.closeMinutes,
          };
          assigned++;
        }
      }
    }

    result.ok = assigned > 0 && result.byDay.some(Boolean);
    return result;
  }

  function detroitNow() {
    var fmt = new Intl.DateTimeFormat("en-US", {
      timeZone: "America/Detroit",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hourCycle: "h23",
      weekday: "short",
    });
    var parts = fmt.formatToParts(new Date());
    var map = {};
    parts.forEach(function (p) {
      if (p.type !== "literal") map[p.type] = p.value;
    });
    var y = parseInt(map.year, 10);
    var mo = parseInt(map.month, 10) - 1;
    var d = parseInt(map.day, 10);
    var h = parseInt(map.hour, 10);
    var mi = parseInt(map.minute, 10);
    var s = parseInt(map.second, 10);
    var carrier = new Date(Date.UTC(y, mo, d, h, mi, s));
    carrier._detroitWeekday = new Date(y, mo, d).getDay();
    var wd = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }[
      map.weekday
    ];
    if (wd != null) carrier._detroitWeekday = wd;
    carrier._y = y;
    carrier._mo = mo;
    carrier._d = d;
    return carrier;
  }

  function todayDayIndex() {
    return detroitNow()._detroitWeekday;
  }

  function weekStartingToday() {
    var start = todayDayIndex();
    var days = [];
    for (var i = 0; i < 7; i++) {
      var idx = (start + i) % 7;
      days.push({
        index: idx,
        short: DAY_SHORT[idx],
        name: DAY_NAMES[idx],
        isToday: i === 0,
      });
    }
    return days;
  }

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function monthDayFromParts(y, mo, d) {
    return pad2(mo + 1) + "-" + pad2(d);
  }

  function monthDayInRange(md, from, through) {
    if (!from || !through) return true;
    if (from <= through) return md >= from && md <= through;
    return md >= from || md <= through;
  }

  function thanksgivingMD(year) {
    // 4th Thursday of November
    var first = new Date(year, 10, 1);
    var dow = first.getDay();
    var firstThu = 1 + ((4 - dow + 7) % 7);
    var day = firstThu + 21;
    return "11-" + pad2(day);
  }

  function easterMD(year) {
    // Anonymous Gregorian algorithm
    var a = year % 19;
    var b = Math.floor(year / 100);
    var c = year % 100;
    var d = Math.floor(b / 4);
    var e = b % 4;
    var f = Math.floor((b + 8) / 25);
    var g = Math.floor((b - f + 1) / 3);
    var h = (19 * a + b - d - g + 15) % 30;
    var i = Math.floor(c / 4);
    var k = c % 4;
    var l = (32 + 2 * e + 2 * i - h - k) % 7;
    var m = Math.floor((a + 11 * h + 22 * l) / 451);
    var month = Math.floor((h + l - 7 * m + 114) / 31);
    var day = ((h + l - 7 * m + 114) % 31) + 1;
    return pad2(month) + "-" + pad2(day);
  }

  function laborDayMD(year) {
    // First Monday of September
    var first = new Date(year, 8, 1);
    var dow = first.getDay();
    var day = 1 + ((1 - dow + 7) % 7);
    return "09-" + pad2(day);
  }

  function resolveHolidayMonthDay(closure, year) {
    if (closure.monthDay) return closure.monthDay;
    var id = (closure.id || closure.name || "").toLowerCase();
    if (id === "thanksgiving" || closure.relativeTo === "thanksgiving") {
      return thanksgivingMD(year);
    }
    if (closure.relativeTo === "thanksgiving+1") {
      var t = thanksgivingMD(year);
      var parts = t.split("-");
      var day = parseInt(parts[1], 10) + 1;
      return "11-" + pad2(day);
    }
    if (id === "easter") return easterMD(year);
    if (id === "labor-day" || id === "labor day") return laborDayMD(year);
    if (id.indexOf("christmas-eve") >= 0 || id === "christmas eve") return "12-24";
    if (id.indexOf("christmas") >= 0) return "12-25";
    if (id.indexOf("new-years-eve") >= 0 || id === "new year's eve") return "12-31";
    if (id.indexOf("new-years") >= 0 || id.indexOf("new year") >= 0) return "01-01";
    return null;
  }

  function isHolidayClosed(venue, carrier) {
    var closures = (venue && venue.holidayClosures) || [];
    var ranges = (venue && venue.holidayRanges) || [];
    var md = monthDayFromParts(carrier._y, carrier._mo, carrier._d);
    var i;
    for (i = 0; i < closures.length; i++) {
      var cmd = resolveHolidayMonthDay(closures[i], carrier._y);
      if (cmd && cmd === md) return true;
    }
    for (i = 0; i < ranges.length; i++) {
      var r = ranges[i];
      if (r.from && r.through && monthDayInRange(md, r.from, r.through)) {
        return true;
      }
    }
    return false;
  }

  function holidayHoursOverride(venue, carrier) {
    var list = (venue && venue.holidayHours) || [];
    var md = monthDayFromParts(carrier._y, carrier._mo, carrier._d);
    for (var i = 0; i < list.length; i++) {
      var h = list[i];
      var cmd = resolveHolidayMonthDay(h, carrier._y);
      if (cmd && cmd === md && h.hours) return h.hours;
    }
    return null;
  }

  function pickSchedule(schedules, carrier) {
    if (!schedules || !schedules.length) return null;
    var md = monthDayFromParts(carrier._y, carrier._mo, carrier._d);
    // Prefer the most specific (shortest) matching range
    var matches = [];
    for (var i = 0; i < schedules.length; i++) {
      var s = schedules[i];
      if (monthDayInRange(md, s.validFrom || "01-01", s.validThrough || "12-31")) {
        matches.push(s);
      }
    }
    if (!matches.length) return null;
    matches.sort(function (a, b) {
      function span(x) {
        var from = x.validFrom || "01-01";
        var through = x.validThrough || "12-31";
        if (from <= through) {
          var aParts = from.split("-").map(Number);
          var bParts = through.split("-").map(Number);
          return bParts[0] * 31 + bParts[1] - (aParts[0] * 31 + aParts[1]);
        }
        return 200; // wrap ranges are long
      }
      return span(a) - span(b);
    });
    return matches[0];
  }

  /**
   * Resolve a venue record (from data JSON / venue-hours-data) for a date.
   * @returns parsed-like object with status fields
   */
  function resolveVenueHours(venue, dateCarrier) {
    var carrier = dateCarrier || detroitNow();
    var status = (venue && venue.hoursStatus) || "verified";
    var checkedAt = (venue && venue.hoursCheckedAt) || null;
    var source = (venue && venue.hoursSource) || null;
    var note = (venue && venue.hoursNote) || null;
    var base = {
      ok: false,
      raw: (venue && venue.hours) || "",
      seasonal: true,
      note: note,
      byDay: [null, null, null, null, null, null, null],
      missingLabel: MISSING_LABEL,
      hoursStatus: status,
      checkedAt: checkedAt,
      source: source,
      schedule: null,
      holidayClosed: false,
      displayHours: (venue && venue.hours) || "",
    };

    if (status === "call-ahead") {
      base.missingLabel = CALL_AHEAD_LABEL;
      // Still parse display hours if present for the weekly table, but
      // dayStatus will treat as unknown unless we explicitly allow.
      if (base.raw) {
        var soft = parseHours(base.raw);
        if (soft.ok) {
          base.byDay = soft.byDay;
          base.raw = soft.raw;
          // ok stays false so open-filter excludes them
        }
      }
      return base;
    }

    if (isHolidayClosed(venue, carrier)) {
      base.holidayClosed = true;
      base.ok = true;
      base.displayHours = "Closed for holiday";
      base.raw = "Closed for holiday";
      return base;
    }

    var override = holidayHoursOverride(venue, carrier);
    if (override) {
      var oh = parseHours(override);
      oh.hoursStatus = status;
      oh.checkedAt = checkedAt;
      oh.source = source;
      oh.schedule = { id: "holiday-hours", hours: override };
      oh.holidayClosed = false;
      oh.displayHours = override;
      return oh;
    }

    var schedules = (venue && venue.hoursSchedules) || [];
    var picked = pickSchedule(schedules, carrier);

    if (status === "closed-season") {
      if (!picked) {
        base.ok = true; // known closed
        base.displayHours = CLOSED_SEASON_LABEL;
        base.raw = CLOSED_SEASON_LABEL;
        base.missingLabel = CLOSED_SEASON_LABEL;
        return base;
      }
    }

    var hoursStr = null;
    if (picked) {
      hoursStr = picked.hours;
      base.schedule = picked;
    } else if (schedules.length) {
      // Seasonal schedules exist but none cover today → call ahead
      base.hoursStatus = "call-ahead";
      base.missingLabel = CALL_AHEAD_LABEL;
      base.note =
        (note ? note + " " : "") +
        "No published hours for this date — call ahead.";
      return base;
    } else if (venue && venue.hours) {
      hoursStr = venue.hours;
    }

    if (!hoursStr) {
      if (status === "closed-season") {
        base.ok = true;
        base.displayHours = CLOSED_SEASON_LABEL;
        return base;
      }
      base.hoursStatus = "call-ahead";
      base.missingLabel = CALL_AHEAD_LABEL;
      return base;
    }

    var parsed = parseHours(hoursStr);
    parsed.hoursStatus = status;
    parsed.checkedAt = checkedAt;
    parsed.source = source;
    parsed.schedule = picked;
    parsed.holidayClosed = false;
    parsed.displayHours = hoursStr;
    parsed.note = note || parsed.note;
    return parsed;
  }

  function dayStatus(parsed, dayIndex) {
    if (!parsed) return "unknown";
    if (parsed.hoursStatus === "call-ahead") return "unknown";
    if (parsed.holidayClosed) return "closed";
    if (parsed.hoursStatus === "closed-season" && !parsed.byDay.some(Boolean)) {
      return "closed";
    }
    if (!parsed.ok) return "unknown";
    return parsed.byDay[dayIndex] ? "open" : "closed";
  }

  function dayHoursLabel(parsed, dayIndex) {
    if (!parsed) return MISSING_LABEL;
    if (parsed.holidayClosed) return "Closed (holiday)";
    if (parsed.hoursStatus === "closed-season" && !parsed.byDay.some(Boolean)) {
      return CLOSED_SEASON_LABEL;
    }
    if (parsed.hoursStatus === "call-ahead") return CALL_AHEAD_LABEL;
    if (!parsed.ok) return parsed.missingLabel || MISSING_LABEL;
    var slot = parsed.byDay[dayIndex];
    if (!slot) return "Closed";
    return slot.label;
  }

  function weeklyRows(parsed) {
    if (!parsed) return null;
    if (parsed.hoursStatus === "call-ahead" && !parsed.ok) return null;
    if (parsed.holidayClosed) {
      return DAY_NAMES.map(function (name, i) {
        return {
          day: name,
          short: DAY_SHORT[i],
          hours: "Closed (holiday)",
          open: false,
        };
      });
    }
    if (parsed.hoursStatus === "closed-season" && !parsed.byDay.some(Boolean)) {
      return DAY_NAMES.map(function (name, i) {
        return {
          day: name,
          short: DAY_SHORT[i],
          hours: CLOSED_SEASON_LABEL,
          open: false,
        };
      });
    }
    if (!parsed.ok) return null;
    return DAY_NAMES.map(function (name, i) {
      var slot = parsed.byDay[i];
      return {
        day: name,
        short: DAY_SHORT[i],
        hours: slot ? slot.label : "Closed",
        open: !!slot,
      };
    });
  }

  function toOpeningHoursSpecification(parsed, options) {
    options = options || {};
    if (!parsed || !parsed.ok) return null;
    if (parsed.hoursStatus === "call-ahead") return null;
    if (parsed.holidayClosed) return null;
    if (parsed.hoursStatus === "closed-season" && !parsed.byDay.some(Boolean)) {
      return null;
    }

    var specs = [];
    var order = [1, 2, 3, 4, 5, 6, 0];
    var used = {};
    order.forEach(function (di) {
      if (used[di]) return;
      var slot = parsed.byDay[di];
      if (!slot) return;
      var days = [di];
      used[di] = true;
      order.forEach(function (dj) {
        if (used[dj]) return;
        var other = parsed.byDay[dj];
        if (
          other &&
          other.openMinutes === slot.openMinutes &&
          other.closeMinutes === slot.closeMinutes
        ) {
          days.push(dj);
          used[dj] = true;
        }
      });
      var spec = {
        "@type": "OpeningHoursSpecification",
        dayOfWeek: days.map(function (d) {
          return DAY_NAMES[d];
        }),
        opens: formatTime24(slot.opens),
        closes:
          slot.closeMinutes >= 24 * 60
            ? "00:00"
            : formatTime24(slot.closes),
      };
      var sched = parsed.schedule || options.schedule;
      if (sched && sched.validFrom && sched.validThrough) {
        // Recurring seasonal window — Schema.org accepts ISO dates; use a
        // representative current/next year span for crawlers.
        var now = detroitNow();
        var y = now._y;
        var from = sched.validFrom;
        var through = sched.validThrough;
        if (from <= through) {
          spec.validFrom = y + "-" + from;
          spec.validThrough = y + "-" + through;
        } else {
          // wraps year e.g. 11-01 → 04-30
          var md = monthDayFromParts(now._y, now._mo, now._d);
          if (md >= from) {
            spec.validFrom = y + "-" + from;
            spec.validThrough = y + 1 + "-" + through;
          } else {
            spec.validFrom = y - 1 + "-" + from;
            spec.validThrough = y + "-" + through;
          }
        }
      }
      specs.push(spec);
    });
    return specs.length ? specs : null;
  }

  function formatCheckedNote(checkedAt) {
    if (!checkedAt) return null;
    var parts = String(checkedAt).split("-");
    if (parts.length !== 3) return "Hours last checked " + checkedAt;
    var months = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    var mo = parseInt(parts[1], 10) - 1;
    var day = parseInt(parts[2], 10);
    var label = months[mo] + " " + day + ", " + parts[0];
    return "Hours last checked " + label;
  }

  function parseDayQuery(value) {
    if (value == null || value === "") return null;
    var v = String(value).trim().toLowerCase();
    if (v === "today") return todayDayIndex();
    if (DAY_ALIASES[v] != null) return DAY_ALIASES[v];
    return null;
  }

  function lookupVenueMeta(slug) {
    var data = global.TCWT_VENUE_HOURS;
    if (!data || !slug) return null;
    return data[slug] || data[String(slug).toLowerCase()] || null;
  }

  function resolveFromCard(card) {
    var slug =
      (card && card.getAttribute && card.getAttribute("data-hours-slug")) ||
      null;
    if (!slug && card && card.getAttribute) {
      var href = card.getAttribute("href") || "";
      var m = href.match(/\/(wineries|cideries|breweries)\/([^/?#]+)/);
      if (m) slug = m[2];
      if (!slug) {
        var link = card.querySelector && card.querySelector("a[href*='/wineries/'],a[href*='/cideries/'],a[href*='/breweries/']");
        if (link) {
          var hm = (link.getAttribute("href") || "").match(
            /\/(wineries|cideries|breweries)\/([^/?#]+)/
          );
          if (hm) slug = hm[2];
        }
      }
    }
    if (slug === "45-north") slug = "forty-five-north";
    var meta = lookupVenueMeta(slug);
    if (meta) return resolveVenueHours(meta);

    // Fallback: legacy data-hours string only
    var raw =
      (card && card.getAttribute && card.getAttribute("data-hours")) || "";
    var statusAttr =
      (card && card.getAttribute && card.getAttribute("data-hours-status")) ||
      "";
    var checked =
      (card &&
        card.getAttribute &&
        card.getAttribute("data-hours-checked")) ||
      null;
    if (statusAttr === "call-ahead" || statusAttr === "closed-season") {
      return resolveVenueHours({
        hours: raw,
        hoursStatus: statusAttr,
        hoursCheckedAt: checked,
        hoursSchedules: [],
      });
    }
    var parsed = parseHours(raw);
    parsed.hoursStatus = "verified";
    parsed.checkedAt = checked;
    parsed.displayHours = raw;
    return parsed;
  }

  global.TCWT_HOURS = {
    DAY_NAMES: DAY_NAMES,
    DAY_SHORT: DAY_SHORT,
    MISSING_LABEL: MISSING_LABEL,
    CALL_AHEAD_LABEL: CALL_AHEAD_LABEL,
    CLOSED_SEASON_LABEL: CLOSED_SEASON_LABEL,
    SEASONAL_NOTE: SEASONAL_NOTE,
    parseHours: parseHours,
    resolveVenueHours: resolveVenueHours,
    resolveFromCard: resolveFromCard,
    lookupVenueMeta: lookupVenueMeta,
    dayStatus: dayStatus,
    dayHoursLabel: dayHoursLabel,
    weeklyRows: weeklyRows,
    toOpeningHoursSpecification: toOpeningHoursSpecification,
    formatCheckedNote: formatCheckedNote,
    todayDayIndex: todayDayIndex,
    weekStartingToday: weekStartingToday,
    parseDayQuery: parseDayQuery,
    detroitNow: detroitNow,
    normalize: normalize,
    monthDayInRange: monthDayInRange,
    pickSchedule: pickSchedule,
  };
})(typeof window !== "undefined" ? window : globalThis);
