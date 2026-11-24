/**
 * Conservative free-text hours parser for Traverse City Wine Tour venue listings.
 * Source strings come from data-*.json only — never invent schedules.
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
      // Bare hour like "3–10pm" left side: infer later from right-side mer
      if (hour > 23) return null;
    }
    return { hour: hour, minute: minute, mer: mer, raw: token };
  }

  function applyMeridiem(left, right) {
    // If left lacks am/pm, inherit from right (e.g. 12–6pm, 3–11pm)
    if (left.mer || !right.mer) return left;
    var hour = left.hour;
    var mer = right.mer;
    // For ranges like 11–12am (closes midnight), left is usually pm previous day —
    // our listings don't use that pattern; treat inherited mer as same period unless
    // left hour > right hour with pm close (e.g. 11–2am) which we reject as ambiguous.
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
    // Strip trailing parentheticals already handled upstream; still guard
    cleaned = cleaned.replace(/\([^)]*\)\s*$/g, "").trim();
    var m = cleaned.match(
      /^(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*-\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))$/i
    );
    if (!m) {
      // Also allow both sides with meridiem or bare close like 12-12am
      m = cleaned.match(
        /^(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*-\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)$/i
      );
    }
    if (!m) return null;
    var right = parseTimeToken(m[2]);
    var left = parseTimeToken(m[1]);
    if (!left || !right) return null;
    if (!right.mer && !left.mer) return null; // too ambiguous
    if (!right.mer && left.mer) {
      // rare: 10am–6 — reject
      return null;
    }
    left = applyMeridiem(left, right);
    if (!left) return null;
    // Midnight close written as 12am
    var openM = toMinutes(left);
    var closeM = toMinutes(right);
    if (closeM === 0 && /12\s*am/i.test(m[2])) closeM = 24 * 60;
    if (closeM <= openM) {
      // overnight e.g. 3pm–1am — allow if close is early morning
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

    // Split segments on middle dot
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
      // Day part + time part: "Mon-Sat 10am-6pm" or "Daily 10am-6pm"
      var dm = seg.match(
        /^((?:daily|every\s*day|everyday|[A-Za-z]+(?:\s*-\s*[A-Za-z]+)?(?:\s*,\s*[A-Za-z]+(?:\s*-\s*[A-Za-z]+)?)*)\s+)(\d.+)$/i
      );
      if (!dm) return result; // unparseable segment → fail whole string conservatively
      var dayPart = dm[1].trim();
      var timePart = dm[2].trim();
      var time = parseTimeRange(timePart);
      if (!time) return result;

      // Support comma-separated day lists: "Mon, Wed, Fri"
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

    // Must have at least one day assigned
    result.ok = assigned > 0 && result.byDay.some(Boolean);
    return result;
  }

  function detroitNow() {
    // Build a Date whose local getters reflect America/Detroit wall time
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
    // Use UTC date object as a carrier for Detroit wall-clock fields
    var carrier = new Date(Date.UTC(y, mo, d, h, mi, s));
    carrier._detroitWeekday = new Date(y, mo, d).getDay(); // local construction for weekday
    // Prefer weekday from formatter
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

  /**
   * Status for a parsed schedule on a given day index (0=Sun).
   * @returns {'open'|'closed'|'unknown'}
   */
  function dayStatus(parsed, dayIndex) {
    if (!parsed || !parsed.ok) return "unknown";
    return parsed.byDay[dayIndex] ? "open" : "closed";
  }

  function dayHoursLabel(parsed, dayIndex) {
    if (!parsed || !parsed.ok) return parsed ? parsed.missingLabel : MISSING_LABEL;
    var slot = parsed.byDay[dayIndex];
    if (!slot) return "Closed";
    return slot.label;
  }

  function weeklyRows(parsed) {
    if (!parsed || !parsed.ok) return null;
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

  function toOpeningHoursSpecification(parsed) {
    if (!parsed || !parsed.ok) return null;
    // Group consecutive same hours
    var specs = [];
    var i = 0;
    // Iterate Mon-Sun for schema friendliness, still cover all days present
    var order = [1, 2, 3, 4, 5, 6, 0];
    var used = {};
    order.forEach(function (di) {
      if (used[di]) return;
      var slot = parsed.byDay[di];
      if (!slot) return;
      var days = [di];
      used[di] = true;
      // gather other days with identical open/close
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
      specs.push({
        "@type": "OpeningHoursSpecification",
        dayOfWeek: days.map(function (d) {
          return DAY_NAMES[d];
        }),
        opens: formatTime24(slot.opens),
        closes:
          slot.closeMinutes >= 24 * 60
            ? "00:00"
            : formatTime24(slot.closes),
      });
    });
    return specs.length ? specs : null;
  }

  function parseDayQuery(value) {
    if (value == null || value === "") return null;
    var v = String(value).trim().toLowerCase();
    if (v === "today") return todayDayIndex();
    if (DAY_ALIASES[v] != null) return DAY_ALIASES[v];
    // full names already in aliases
    return null;
  }

  global.TCWT_HOURS = {
    DAY_NAMES: DAY_NAMES,
    DAY_SHORT: DAY_SHORT,
    MISSING_LABEL: MISSING_LABEL,
    SEASONAL_NOTE: SEASONAL_NOTE,
    parseHours: parseHours,
    dayStatus: dayStatus,
    dayHoursLabel: dayHoursLabel,
    weeklyRows: weeklyRows,
    toOpeningHoursSpecification: toOpeningHoursSpecification,
    todayDayIndex: todayDayIndex,
    weekStartingToday: weekStartingToday,
    parseDayQuery: parseDayQuery,
    detroitNow: detroitNow,
    normalize: normalize,
  };
})(typeof window !== "undefined" ? window : globalThis);
