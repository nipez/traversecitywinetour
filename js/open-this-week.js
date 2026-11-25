/**
 * "Open this week" day picker for directory pages and the winery map.
 * Requires js/hours.js (TCWT_HOURS). Cards need data-hours="...".
 *
 * Mount: <div id="openThisWeek" data-otw-scope="directory"></div>
 * Optional: data-otw-map="1" for map-only mode (dispatches tcwt:open-day events).
 */
(function () {
  var H = window.TCWT_HOURS;
  if (!H) return;

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }
  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function selectedDayFromUrl() {
    var params = new URLSearchParams(window.location.search);
    var fromQuery = H.parseDayQuery(params.get("day"));
    if (fromQuery != null) return fromQuery;
    var hash = (window.location.hash || "").replace(/^#/, "").toLowerCase();
    if (hash.indexOf("open-this-week") === 0) {
      var parts = hash.split("=");
      if (parts[1]) {
        var d = H.parseDayQuery(parts[1]);
        if (d != null) return d;
      }
      return H.todayDayIndex();
    }
    return H.todayDayIndex();
  }

  function buildStyles() {
    if (document.getElementById("otw-styles")) return;
    var css = document.createElement("style");
    css.id = "otw-styles";
    css.textContent =
      "#open-this-week,.otw-bar{scroll-margin-top:100px;}" +
      ".otw-bar{background:var(--cream,#F5F0E8);border-bottom:1px solid rgba(74,14,27,0.08);padding:14px 40px;}" +
      ".otw-inner{max-width:1340px;margin:0 auto;}" +
      ".peninsula-section .otw-bar{margin-bottom:16px;border:1px solid rgba(74,14,27,0.08);border-radius:8px;}" +
      ".otw-top{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:10px 24px;margin-bottom:12px;}" +
      ".otw-title{font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--burgundy,#4A0E1B);font-weight:600;margin:0;}" +
      ".otw-note{font-size:0.78rem;color:var(--text-light,#6B5E54);line-height:1.45;max-width:42rem;}" +
      ".otw-days{display:flex;flex-wrap:wrap;gap:8px;align-items:center;}" +
      ".otw-day{appearance:none;border:1px solid rgba(74,14,27,0.15);background:var(--white,#fff);color:var(--text,#3D2C29);font-family:'Outfit',sans-serif;font-size:0.72rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;padding:10px 14px;border-radius:4px;cursor:pointer;transition:border-color .2s,background .2s,color .2s;}" +
      ".otw-day:hover{border-color:var(--burgundy,#4A0E1B);color:var(--burgundy,#4A0E1B);}" +
      ".otw-day[aria-pressed='true']{background:var(--burgundy,#4A0E1B);border-color:var(--burgundy,#4A0E1B);color:var(--cream,#F5F0E8);}" +
      ".otw-day.is-today:not([aria-pressed='true']){border-color:rgba(201,169,110,0.7);}" +
      ".otw-meta{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;margin-top:12px;}" +
      ".otw-count{font-size:0.8rem;color:var(--burgundy,#4A0E1B);font-weight:600;}" +
      ".otw-toggle{display:inline-flex;align-items:center;gap:8px;font-size:0.78rem;color:var(--text,#3D2C29);cursor:pointer;user-select:none;}" +
      ".otw-toggle input{accent-color:var(--burgundy,#4A0E1B);}" +
      ".otw-badge{display:inline-flex;align-items:center;gap:6px;font-size:0.65rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;padding:3px 8px;border-radius:3px;margin-left:8px;vertical-align:middle;}" +
      ".otw-badge.open{background:rgba(45,90,61,0.12);color:#2D5A3D;}" +
      ".otw-badge.closed{background:rgba(74,14,27,0.08);color:#6B5E54;}" +
      ".otw-badge.unknown{background:rgba(201,169,110,0.18);color:#8a6a2a;}" +
      ".otw-day-hours{font-size:0.72rem;color:var(--text-light,#6B5E54);margin-top:4px;}" +
      ".otw-checked{font-size:0.72rem;color:var(--text-light,#6B5E54);}" +
      ".winery-card.otw-dim{opacity:0.38;}" +
      ".sidebar-detail[data-hours-block]{flex-direction:column;align-items:stretch;gap:8px;}" +
      ".sidebar-detail[data-hours-block] > svg{display:none;}" +
      ".winery-hours-week{margin-top:4px;width:100%;border-collapse:collapse;font-size:0.85rem;}" +
      ".winery-hours-week th,.winery-hours-week td{padding:6px 0;border-bottom:1px solid rgba(74,14,27,0.06);text-align:left;white-space:nowrap;}" +
      ".winery-hours-week th{font-weight:600;color:var(--burgundy,#4A0E1B);width:3.2rem;padding-right:12px;}" +
      ".winery-hours-week tr.is-today th,.winery-hours-week tr.is-today td{color:var(--burgundy,#4A0E1B);font-weight:600;}" +
      ".winery-hours-note{display:block;margin-top:10px;font-size:0.78rem;color:var(--text-light,#6B5E54);line-height:1.45;}" +
      ".winery-hours-checked{display:block;margin-top:6px;font-size:0.72rem;color:var(--text-light,#6B5E54);}" +
      "@media(max-width:768px){" +
      "#open-this-week,.otw-bar{scroll-margin-top:230px;}" +
      ".otw-bar{padding:12px 16px;}" +
      ".otw-day{padding:9px 11px;font-size:0.68rem;}" +
      "}";
    document.head.appendChild(css);
  }

  function latestCheckedLabel() {
    var data = window.TCWT_VENUE_HOURS || {};
    var latest = null;
    Object.keys(data).forEach(function (k) {
      var c = data[k] && data[k].hoursCheckedAt;
      if (c && (!latest || c > latest)) latest = c;
    });
    return H.formatCheckedNote(latest);
  }

  function renderBar(mount, state) {
    var week = H.weekStartingToday();
    var daysHtml = week
      .map(function (d) {
        return (
          '<button type="button" class="otw-day' +
          (d.isToday ? " is-today" : "") +
          '" data-day="' +
          d.index +
          '" aria-pressed="' +
          (state.day === d.index ? "true" : "false") +
          '">' +
          d.short +
          (d.isToday ? " · Today" : "") +
          "</button>"
        );
      })
      .join("");
    var checked = latestCheckedLabel();

    mount.innerHTML =
      '<div class="otw-bar" id="open-this-week">' +
      '<div class="otw-inner">' +
      '<div class="otw-top">' +
      '<h2 class="otw-title">Open this week</h2>' +
      '<p class="otw-note">' +
      H.SEASONAL_NOTE +
      (checked
        ? ' <span class="otw-checked">' + checked + ".</span>"
        : "") +
      "</p>" +
      "</div>" +
      '<div class="otw-days" role="group" aria-label="Choose a day">' +
      daysHtml +
      "</div>" +
      '<div class="otw-meta">' +
      '<label class="otw-toggle"><input type="checkbox" id="otwOnlyOpen"' +
      (state.onlyOpen ? " checked" : "") +
      "> Show only open</label>" +
      '<div class="otw-count" id="otwCount" aria-live="polite"></div>' +
      "</div>" +
      "</div>" +
      "</div>";
  }

  function badgeLabel(status) {
    if (status === "open") return "Open";
    if (status === "closed") return "Closed";
    return "Call ahead";
  }

  function resolveCard(card) {
    if (typeof H.resolveFromCard === "function") return H.resolveFromCard(card);
    return H.parseHours(card.getAttribute("data-hours") || "");
  }

  function cardHours(card) {
    return card.getAttribute("data-hours") || "";
  }

  function applyDirectory(state) {
    var cards = qsa(
      "a.winery-card[data-hours], div.venue-card[data-hours], .winery-card[data-hours]"
    );
    var open = 0;
    var closed = 0;
    var unknown = 0;
    var mount = qs("#openThisWeek");
    var mapScope = mount && mount.getAttribute("data-otw-scope") === "map";

    if (mapScope && Array.isArray(window.wineries)) {
      window.wineries.forEach(function (w) {
        var meta =
          (w.slug && H.lookupVenueMeta && H.lookupVenueMeta(w.slug)) ||
          (w.name &&
            window.TCWT_VENUE_HOURS &&
            Object.keys(window.TCWT_VENUE_HOURS).map(function (k) {
              return window.TCWT_VENUE_HOURS[k];
            }).find(function (m) {
              return m && m.name === w.name;
            })) ||
          {
            hours: w.hours || "",
            hoursStatus: w.hoursStatus || "verified",
            hoursCheckedAt: w.hoursCheckedAt,
            hoursSchedules: w.hoursSchedules || [],
            holidayClosures: w.holidayClosures || [],
          };
        var parsed = H.resolveVenueHours
          ? H.resolveVenueHours(meta)
          : H.parseHours(w.hours || "");
        w._parsed = parsed;
        var status = H.dayStatus(parsed, state.day);
        if (status === "open") open++;
        else if (status === "closed") closed++;
        else unknown++;
      });
      var countElMap = qs("#otwCount");
      if (countElMap) {
        countElMap.textContent =
          open +
          " open on map · " +
          closed +
          " closed · " +
          unknown +
          " call ahead";
      }
      document.dispatchEvent(
        new CustomEvent("tcwt:open-day", {
          detail: { day: state.day, onlyOpen: state.onlyOpen },
        })
      );
      return;
    }

    cards.forEach(function (card) {
      var parsed = resolveCard(card);
      var status = H.dayStatus(parsed, state.day);
      var label = H.dayHoursLabel(parsed, state.day);

      var badge = card.querySelector(".otw-badge");
      if (!badge) {
        badge = document.createElement("span");
        badge.className = "otw-badge";
        var nameEl = card.querySelector(".winery-name, .venue-name, h3");
        if (nameEl) nameEl.appendChild(badge);
        else card.appendChild(badge);
      }
      badge.className = "otw-badge " + status;
      badge.textContent = badgeLabel(status);

      var dayLine = card.querySelector(".otw-day-hours");
      if (!dayLine) {
        dayLine = document.createElement("div");
        dayLine.className = "otw-day-hours";
        var hoursEl = card.querySelector(".winery-hours, .venue-hours");
        if (hoursEl && hoursEl.parentNode) {
          hoursEl.parentNode.insertBefore(dayLine, hoursEl.nextSibling);
        } else {
          card.appendChild(dayLine);
        }
      }
      dayLine.textContent =
        status === "unknown"
          ? label
          : H.DAY_SHORT[state.day] + ": " + label;

      if (status === "open") open++;
      else if (status === "closed") closed++;
      else unknown++;

      var hide =
        state.onlyOpen && status !== "open"
          ? true
          : false;
      if (hide) {
        card.style.display = "none";
        card.classList.remove("otw-dim");
      } else {
        if (card.style.display === "none" && card.dataset.otwHidden === "1") {
          card.style.display = "";
        }
        card.dataset.otwHidden = hide ? "1" : "0";
        card.classList.toggle(
          "otw-dim",
          state.onlyOpen === false && (status === "closed" || status === "unknown")
        );
      }
      if (state.onlyOpen) {
        card.dataset.otwHidden = hide ? "1" : "0";
        if (hide) card.style.display = "none";
        else if (card.dataset.otwForcedShow !== "0") card.style.display = "";
      }
    });

    var countEl = qs("#otwCount");
    if (countEl) {
      countEl.textContent =
        open +
        " open · " +
        closed +
        " closed · " +
        unknown +
        " call ahead";
    }

    // Section visibility when only-open
    ["sec-old", "sec-lee", "sec-venues"].forEach(function (id) {
      var sec = document.getElementById(id);
      if (!sec) return;
      if (!state.onlyOpen) return;
      var visible = qsa(".winery-card, .venue-card", sec).some(function (c) {
        return c.style.display !== "none";
      });
      var head = sec.querySelector(".winery-section-head, .pen-header");
      if (head) head.style.display = visible ? "" : "none";
    });

    document.dispatchEvent(
      new CustomEvent("tcwt:open-day", {
        detail: { day: state.day, onlyOpen: state.onlyOpen },
      })
    );
  }

  function wire(mount, state) {
    mount.addEventListener("click", function (e) {
      var btn = e.target.closest(".otw-day");
      if (!btn) return;
      state.day = parseInt(btn.getAttribute("data-day"), 10);
      qsa(".otw-day", mount).forEach(function (b) {
        b.setAttribute(
          "aria-pressed",
          b === btn ? "true" : "false"
        );
      });
      applyDirectory(state);
      try {
        var short = H.DAY_SHORT[state.day].toLowerCase();
        history.replaceState(
          null,
          "",
          window.location.pathname + "?day=" + short + "#open-this-week"
        );
      } catch (err) {}
    });
    mount.addEventListener("change", function (e) {
      if (e.target && e.target.id === "otwOnlyOpen") {
        state.onlyOpen = !!e.target.checked;
        applyDirectory(state);
      }
    });
  }

  function enhanceDetailSidebar() {
    var host = qs("[data-hours-block]");
    if (!host) return;
    var slug = host.getAttribute("data-hours-slug");
    var meta = slug && H.lookupVenueMeta ? H.lookupVenueMeta(slug) : null;
    var parsed = meta
      ? H.resolveVenueHours(meta)
      : H.parseHours(host.getAttribute("data-hours") || host.textContent);
    var rows = H.weeklyRows(parsed);
    var today = H.todayDayIndex();
    var checked = H.formatCheckedNote(parsed.checkedAt || host.getAttribute("data-hours-checked"));
    var checkedHtml = checked
      ? '<span class="winery-hours-checked">' + checked + "</span>"
      : "";
    if (!rows) {
      var missing =
        parsed.hoursStatus === "call-ahead"
          ? H.CALL_AHEAD_LABEL
          : parsed.hoursStatus === "closed-season"
            ? H.CLOSED_SEASON_LABEL
            : H.MISSING_LABEL;
      host.innerHTML =
        "<div>" +
        missing +
        '</div><p class="winery-hours-note">' +
        H.SEASONAL_NOTE +
        (parsed.note ? " " + parsed.note : "") +
        "</p>" +
        checkedHtml;
      return;
    }
    var table =
      '<table class="winery-hours-week" aria-label="Weekly hours"><tbody>' +
      rows
        .map(function (r, i) {
          return (
            '<tr class="' +
            (i === today ? "is-today" : "") +
            '"><th scope="row">' +
            r.short +
            "</th><td>" +
            r.hours +
            "</td></tr>"
          );
        })
        .join("") +
      "</tbody></table>";
    var note =
      '<p class="winery-hours-note">' +
      H.SEASONAL_NOTE +
      (parsed.note ? " (" + parsed.note + ")" : "") +
      "</p>";
    host.innerHTML =
      "<div><strong style=\"display:block;margin-bottom:6px;color:var(--burgundy,#4A0E1B);font-size:0.82rem;letter-spacing:0.04em;text-transform:uppercase;\">Hours</strong>" +
      table +
      note +
      checkedHtml +
      "</div>";
  }

  function init() {
    buildStyles();
    enhanceDetailSidebar();
    var mount = qs("#openThisWeek");
    if (!mount) return;
    var state = {
      day: selectedDayFromUrl(),
      onlyOpen: true,
    };
    // Default onlyOpen true when arriving via open-this-week deep link
    var hash = (window.location.hash || "").toLowerCase();
    var params = new URLSearchParams(window.location.search);
    if (!hash.includes("open-this-week") && !params.has("day")) {
      state.onlyOpen = false;
    }
    renderBar(mount, state);
    wire(mount, state);
    applyDirectory(state);

    // Re-apply after peninsula/search filters if the page exposes applyFilters
    var origApply = window.applyFilters;
    if (typeof origApply === "function") {
      window.applyFilters = function () {
        origApply.apply(this, arguments);
        applyDirectory(state);
      };
    }

    // Deep links: keep the bar clear of the sticky nav
    if (
      (window.location.hash || "").toLowerCase().indexOf("open-this-week") >= 0 ||
      new URLSearchParams(window.location.search).has("day")
    ) {
      var bar = qs("#open-this-week");
      if (bar) {
        setTimeout(function () {
          bar.scrollIntoView({ block: "start", behavior: "instant" in window ? "instant" : "auto" });
        }, 50);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
