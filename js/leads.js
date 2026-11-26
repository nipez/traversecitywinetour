(function () {
  const API = "/api/leads";

  function privacyHref() {
    return "/privacy";
  }

  function utm() {
    const params = new URLSearchParams(window.location.search);
    return {
      utm_source: params.get("utm_source") || "",
      utm_medium: params.get("utm_medium") || "",
      utm_campaign: params.get("utm_campaign") || "",
    };
  }

  function ensureHoneypot(form) {
    if (form.querySelector('[name="hp"]')) return;
    const trap = document.createElement("input");
    trap.type = "text";
    trap.name = "hp";
    trap.tabIndex = -1;
    trap.autocomplete = "off";
    trap.setAttribute("aria-hidden", "true");
    trap.style.cssText = "position:absolute;left:-9999px;opacity:0;height:0;width:0;";
    form.appendChild(trap);
  }

  function ensureConsent(form, compact) {
    if (form.querySelector('[name="consent"]')) return;
    const wrap = document.createElement("label");
    wrap.className = compact ? "lead-consent lead-consent-compact" : "lead-consent";
    wrap.innerHTML =
      '<input type="checkbox" name="consent" value="true" required>' +
      "<span>I agree to the <a href=\"" +
      privacyHref() +
      '">Privacy Policy</a> and to being contacted about this request.</span>';
    const button = form.querySelector('button[type="submit"], .form-submit');
    if (!button) {
      form.appendChild(wrap);
    } else if (compact) {
      button.insertAdjacentElement("afterend", wrap);
    } else {
      form.insertBefore(wrap, button);
    }
  }

  function setStatus(form, message, kind) {
    let el = form.querySelector(".lead-status");
    if (!el) {
      el = document.createElement("p");
      el.className = "lead-status";
      el.setAttribute("role", "status");
      form.appendChild(el);
    }
    el.textContent = message || "";
    el.dataset.kind = kind || "";
  }

  function collectPayload(form, type) {
    const data = new FormData(form);
    const payload = {};
    for (const [key, value] of data.entries()) {
      if (["email", "name", "consent", "hp", "company_url", "type"].includes(key)) continue;
      payload[key] = String(value || "").trim();
    }
    return {
      type,
      email: String(data.get("email") || "").trim(),
      name: String(data.get("name") || "").trim(),
      consent: data.get("consent") === "true" || data.get("consent") === "on",
      hp: String(data.get("hp") || ""),
      source_page: window.location.pathname,
      payload,
      ...utm(),
    };
  }

  async function submitLead(form, type) {
    const button = form.querySelector('button[type="submit"], .form-submit');
    const original = button ? button.textContent : "";
    if (button) {
      button.disabled = true;
      button.textContent = "Sending…";
    }
    setStatus(form, "", "");

    try {
      const response = await fetch(API, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(collectPayload(form, type)),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(body.error || "Something went wrong. Please try again.");
      }
      return body;
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = original;
      }
    }
  }

  function wireNewsletter(form) {
    form.removeAttribute("onsubmit");
    const email = form.querySelector('input[type="email"]');
    if (email && !email.name) {
      email.name = "email";
      email.required = true;
      email.autocomplete = "email";
    }
    ensureHoneypot(form);
    ensureConsent(form, true);

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        const result = await submitLead(form, "newsletter");
        form.reset();
        const emailInput = form.querySelector('input[type="email"]');
        if (emailInput) emailInput.value = "";
        setStatus(
          form,
          result.already_subscribed
            ? "You're already on the list. We'll keep you posted."
            : "You're in. Watch your inbox for wine-country updates.",
          "ok"
        );
      } catch (error) {
        setStatus(form, error.message || "Could not subscribe right now.", "error");
      }
    });
  }

  function wireLeadForm(form) {
    const type = form.getAttribute("data-lead-form");
    if (!type) return;
    form.removeAttribute("onsubmit");
    ensureHoneypot(form);
    ensureConsent(form, false);

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await submitLead(form, type);
        const success = document.getElementById(form.getAttribute("data-success") || "formSuccess");
        if (success) {
          form.style.display = "none";
          success.style.display = "block";
          return;
        }
        form.reset();
        setStatus(form, "Thanks — we received your request and will follow up shortly.", "ok");
      } catch (error) {
        setStatus(form, error.message || "Could not send your request right now.", "error");
      }
    });
  }

  function injectStyles() {
    if (document.getElementById("lead-form-styles")) return;
    const style = document.createElement("style");
    style.id = "lead-form-styles";
    style.textContent = `
      .lead-consent { display:flex; align-items:flex-start; gap:10px; margin:16px 0 8px; font-size:0.82rem; line-height:1.5; color:inherit; }
      .lead-consent input { flex:0 0 auto; margin-top:3px; accent-color:#4A0E1B; }
      .lead-consent span { flex:1 1 auto; min-width:0; text-align:left; }
      .lead-consent a { color:#C9A96E; }
      .lead-consent-compact { flex:1 1 100%; width:100%; max-width:none; margin:10px 0 0; color:rgba(245,240,232,0.72); justify-content:flex-start; }
      .newsletter-form { flex-wrap:wrap; align-items:center; }
      .newsletter-form input[type="email"] { flex:1 1 180px; min-width:0; }
      .newsletter-form button { flex:0 0 auto; }
      .lead-status { margin-top:12px; font-size:0.88rem; line-height:1.5; }
      .newsletter-form .lead-status { flex:1 1 100%; width:100%; }
      .lead-status[data-kind="ok"] { color:#2f6b3a; }
      .newsletter .lead-status[data-kind="ok"] { color:#D4BC8B; }
      .lead-status[data-kind="error"] { color:#9b2c2c; }
      .newsletter .lead-status[data-kind="error"] { color:#f3c1c1; }

      .winery-tour-cta-band { max-width:1340px; margin:0 auto 8px; padding:0 40px 48px; }
      .winery-tour-cta-band-inner { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:20px; padding:28px 32px; background:linear-gradient(135deg, rgba(74,14,27,0.06), rgba(201,169,110,0.12)); border:1px solid rgba(74,14,27,0.08); border-radius:8px; }
      .winery-tour-cta-copy { flex:1 1 240px; min-width:0; }
      .winery-tour-cta-copy h2 { font-family:'Playfair Display',serif; font-size:1.45rem; font-weight:500; color:#4A0E1B; margin:0 0 8px; }
      .winery-tour-cta-copy p { margin:0; font-size:0.95rem; line-height:1.6; color:#7A7068; }
      .winery-tour-cta { display:inline-flex; align-items:center; justify-content:center; gap:8px; width:auto; min-height:48px; padding:14px 22px; border:none; border-radius:4px; background:#C9A96E; color:#4A0E1B; font-family:'Outfit',sans-serif; font-size:0.78rem; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; text-decoration:none; cursor:pointer; transition:background 0.3s; }
      .winery-tour-cta:hover { background:#D4BC8B; }
      .sidebar-card .winery-tour-cta,
      .info-card .winery-tour-cta { width:100%; margin-top:16px; }
      .sidebar-card .winery-tour-secondary,
      .info-card .winery-tour-secondary,
      .sidebar-card .winery-tour-quote,
      .info-card .winery-tour-quote { display:block; width:100%; text-align:center; margin-top:12px; padding:12px; border:1px solid rgba(74,14,27,0.15); border-radius:4px; background:transparent; color:#4A0E1B; font-family:'Outfit',sans-serif; font-size:0.78rem; font-weight:500; letter-spacing:0.04em; text-decoration:none; cursor:pointer; transition:border-color 0.3s,color 0.3s; }
      .sidebar-card .winery-tour-secondary:hover,
      .info-card .winery-tour-secondary:hover,
      .sidebar-card .winery-tour-quote:hover,
      .info-card .winery-tour-quote:hover { border-color:#4A0E1B; }
      .venue-plan-actions { display:flex; flex-direction:column; gap:0; margin-top:4px; }
      .winery-tour-cta-band-actions { display:flex; flex-wrap:wrap; gap:12px; align-items:center; }
      .winery-tour-cta-band-actions .winery-tour-quote { display:inline-flex; width:auto; margin-top:0; min-height:48px; padding:14px 20px; }

      .tour-quote-overlay { position:fixed; inset:0; z-index:3000; display:flex; align-items:center; justify-content:center; padding:16px; background:rgba(44,36,32,0.6); backdrop-filter:blur(4px); opacity:0; pointer-events:none; transition:opacity 0.25s; }
      .tour-quote-overlay.show { opacity:1; pointer-events:auto; }
      .tour-quote-modal { width:100%; max-width:520px; max-height:92vh; overflow:auto; background:#fff; border-radius:16px; box-shadow:0 24px 80px rgba(74,14,27,0.2); transform:translateY(16px); transition:transform 0.25s; }
      .tour-quote-overlay.show .tour-quote-modal { transform:translateY(0); }
      .tour-quote-top { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:24px 28px; border-bottom:1px solid rgba(74,14,27,0.06); }
      .tour-quote-top h2 { margin:0; font-family:'Playfair Display',serif; font-size:1.2rem; color:#4A0E1B; }
      .tour-quote-close { background:none; border:none; color:#7A7068; cursor:pointer; padding:4px; }
      .tour-quote-close:hover { color:#4A0E1B; }
      .tour-quote-summary { margin:16px 28px 0; padding:14px 16px; background:#F5F0E8; border-radius:8px; border:1px solid rgba(74,14,27,0.06); }
      .tour-quote-summary-label { font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase; color:#7A7068; margin-bottom:6px; }
      .tour-quote-summary-name { font-size:0.92rem; color:#4A0E1B; font-weight:500; line-height:1.4; }
      .tour-quote-form { padding:16px 28px 24px; }
      .tour-quote-form .form-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
      .tour-quote-form .form-group { margin-bottom:12px; }
      .tour-quote-form .form-group.full { grid-column:1 / -1; }
      .tour-quote-form label { display:block; font-size:0.72rem; font-weight:600; letter-spacing:0.04em; margin-bottom:5px; color:#3A3330; }
      .tour-quote-form input:not([type="checkbox"]):not([type="radio"]):not([type="hidden"]),
      .tour-quote-form textarea { width:100%; padding:10px 12px; border:1px solid rgba(74,14,27,0.15); border-radius:6px; font:inherit; font-size:0.9rem; background:#fff; color:#3A3330; }
      .tour-quote-form input[type="checkbox"] { width:auto; min-width:16px; margin-top:3px; accent-color:#4A0E1B; }
      .tour-quote-form textarea { min-height:72px; resize:vertical; }
      .tour-quote-form .form-submit { width:100%; margin-top:4px; padding:12px 20px; background:#4A0E1B; color:#F5F0E8; border:none; border-radius:6px; font-family:'Outfit',sans-serif; font-size:0.82rem; font-weight:600; letter-spacing:0.04em; cursor:pointer; }
      .tour-quote-form .form-submit:hover { background:#6B1A2A; }
      .tour-quote-form .form-submit:disabled { opacity:0.6; cursor:not-allowed; }
      .tour-quote-form .form-note { margin:10px 0 8px; font-size:0.72rem; color:#7A7068; line-height:1.5; }
      .tour-quote-form .form-note a { color:#4A0E1B; }
      .tour-quote-success { display:none; padding:28px; text-align:center; }
      .tour-quote-success h3 { font-family:'Playfair Display',serif; font-size:1.2rem; color:#4A0E1B; margin:0 0 8px; }
      .tour-quote-success p { font-size:0.88rem; color:#7A7068; line-height:1.55; margin:0 0 20px; }
      .tour-quote-success button { padding:10px 20px; background:#4A0E1B; color:#F5F0E8; border:none; border-radius:6px; font-family:'Outfit',sans-serif; font-size:0.78rem; font-weight:600; cursor:pointer; }
      @media (max-width:640px) {
        .winery-tour-cta-band { padding:0 20px 36px; }
        .winery-tour-cta-band-inner { padding:22px 20px; }
        .tour-quote-form .form-row { grid-template-columns:1fr; }
      }
    `;
    document.head.appendChild(style);
  }

  function ensureTourQuoteModal() {
    let overlay = document.getElementById("tourQuoteOverlay");
    if (overlay) return overlay;

    overlay = document.createElement("div");
    overlay.id = "tourQuoteOverlay";
    overlay.className = "tour-quote-overlay";
    overlay.setAttribute("role", "presentation");
    overlay.innerHTML = `
      <div class="tour-quote-modal" role="dialog" aria-modal="true" aria-labelledby="tourQuoteTitle">
        <div class="tour-quote-top">
          <h2 id="tourQuoteTitle">Request a tour quote</h2>
          <button type="button" class="tour-quote-close" aria-label="Close quote form">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="tour-quote-summary">
          <div class="tour-quote-summary-label" id="tourQuoteSummaryLabel">Guided visit including</div>
          <div class="tour-quote-summary-name" id="tourQuoteWineryLabel"></div>
        </div>
        <form class="tour-quote-form" id="tourQuoteForm" data-lead-form="tour" data-success="tourQuoteSuccess">
          <input type="hidden" name="winery" id="tourQuoteWinery" value="">
          <input type="hidden" name="winery_slug" id="tourQuoteWinerySlug" value="">
          <input type="hidden" name="venue" id="tourQuoteVenue" value="">
          <input type="hidden" name="venue_slug" id="tourQuoteVenueSlug" value="">
          <input type="hidden" name="venue_type" id="tourQuoteVenueType" value="">
          <input type="hidden" name="interest" id="tourQuoteInterest" value="">
          <input type="hidden" name="operator" id="tourQuoteOperator" value="">
          <input type="hidden" name="itinerary" id="tourQuoteItinerary" value="">
          <input type="hidden" name="planner_url" id="tourQuotePlannerUrl" value="">
          <div class="form-row">
            <div class="form-group">
              <label for="tour-quote-name">Name</label>
              <input type="text" id="tour-quote-name" name="name" required autocomplete="name">
            </div>
            <div class="form-group">
              <label for="tour-quote-email">Email</label>
              <input type="email" id="tour-quote-email" name="email" required autocomplete="email">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="tour-quote-date">Preferred date</label>
              <input type="date" id="tour-quote-date" name="preferred_date" required>
            </div>
            <div class="form-group">
              <label for="tour-quote-party">Group size</label>
              <input type="number" id="tour-quote-party" name="party_size" min="1" max="50" placeholder="e.g. 6" required>
            </div>
          </div>
          <div class="form-group full">
            <label for="tour-quote-phone">Phone <span style="font-weight:400;color:#7A7068;">(optional)</span></label>
            <input type="tel" id="tour-quote-phone" name="phone" autocomplete="tel">
          </div>
          <div class="form-group full">
            <label for="tour-quote-message">Notes <span style="font-weight:400;color:#7A7068;">(optional)</span></label>
            <textarea id="tour-quote-message" name="message" placeholder="Hotel pickup, occasion, other stops…"></textarea>
          </div>
          <p class="form-note">We’ll match you with a local wine-tour operator. No payment is collected here.</p>
          <button type="submit" class="form-submit">Request tour quote</button>
        </form>
        <div class="tour-quote-success" id="tourQuoteSuccess">
          <h3>Request received</h3>
          <p>Thanks — we received your tour request and will follow up shortly with options.</p>
          <button type="button" id="tourQuoteSuccessClose">Close</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    const form = overlay.querySelector("#tourQuoteForm");
    wireLeadForm(form);

    const close = () => closeTourQuoteModal();
    overlay.querySelector(".tour-quote-close").addEventListener("click", close);
    overlay.querySelector("#tourQuoteSuccessClose").addEventListener("click", close);
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) close();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && overlay.classList.contains("show")) close();
    });

    return overlay;
  }

  function plannerUrlForStop(stopToken) {
    if (!stopToken) return "";
    try {
      const url = new URL("/plan-your-day", window.location.origin);
      url.searchParams.set("stops", stopToken);
      return url.toString();
    } catch {
      return "/plan-your-day?stops=" + encodeURIComponent(stopToken);
    }
  }

  function openTourQuoteModal(opts) {
    if (typeof opts === "string") {
      opts = { winery: opts, winerySlug: arguments[1] || "" };
    }
    opts = opts || {};

    const overlay = ensureTourQuoteModal();
    const form = overlay.querySelector("#tourQuoteForm");
    const success = overlay.querySelector("#tourQuoteSuccess");
    form.style.display = "";
    success.style.display = "none";
    form.reset();
    setStatus(form, "", "");

    const winery = opts.winery || "";
    const winerySlug = opts.winerySlug || "";
    const venue = opts.venue || "";
    const venueSlug = opts.venueSlug || "";
    const venueType = opts.venueType || "";
    const interest = opts.interest || "";
    const plannerStop = opts.plannerStop || winerySlug || venueSlug || "";
    const stopName = winery || venue || "";
    const label =
      opts.label ||
      winery ||
      venue ||
      interest ||
      "a guided Traverse City wine tour";
    const operator =
      opts.operator ||
      (winery
        ? "Driver quote including " + winery
        : venue
          ? "Driver quote including " + venue
          : interest
            ? interest + " quote"
            : "Guided wine tour quote");
    const summaryLabel = interest && !winery && !venue
      ? "Tour interest"
      : stopName
        ? "Driver quote stop"
        : "Guided visit including";
    const itinerary = stopName ? "1. " + stopName : "";
    const plannerUrl = plannerStop ? plannerUrlForStop(plannerStop) : "";

    overlay.querySelector("#tourQuoteTitle").textContent = stopName
      ? "Request a driver quote"
      : "Request a tour quote";
    overlay.querySelector("#tourQuoteSummaryLabel").textContent = summaryLabel;
    overlay.querySelector("#tourQuoteWineryLabel").textContent = label;
    overlay.querySelector("#tourQuoteWinery").value = winery;
    overlay.querySelector("#tourQuoteWinerySlug").value = winerySlug;
    overlay.querySelector("#tourQuoteVenue").value = venue;
    overlay.querySelector("#tourQuoteVenueSlug").value = venueSlug;
    overlay.querySelector("#tourQuoteVenueType").value = venueType;
    overlay.querySelector("#tourQuoteInterest").value = interest;
    overlay.querySelector("#tourQuoteOperator").value = operator;
    overlay.querySelector("#tourQuoteItinerary").value = itinerary;
    overlay.querySelector("#tourQuotePlannerUrl").value = plannerUrl;

    overlay.classList.add("show");
    document.body.style.overflow = "hidden";
    const first = overlay.querySelector("#tour-quote-name");
    if (first) first.focus();
  }

  function closeTourQuoteModal() {
    const overlay = document.getElementById("tourQuoteOverlay");
    if (!overlay) return;
    overlay.classList.remove("show");
    document.body.style.overflow = "";
  }

  function wireTourQuoteTriggers() {
    const triggers = document.querySelectorAll("[data-tour-quote]");
    if (!triggers.length) return;
    ensureTourQuoteModal();
    triggers.forEach((el) => {
      el.addEventListener("click", (event) => {
        event.preventDefault();
        openTourQuoteModal({
          winery: el.getAttribute("data-winery-name") || "",
          winerySlug: el.getAttribute("data-winery-slug") || "",
          venue: el.getAttribute("data-venue-name") || "",
          venueSlug: el.getAttribute("data-venue-slug") || "",
          venueType: el.getAttribute("data-venue-type") || "",
          interest: el.getAttribute("data-tour-interest") || "",
          operator: el.getAttribute("data-operator") || "",
          label: el.getAttribute("data-tour-label") || "",
          plannerStop: el.getAttribute("data-planner-stop") || "",
        });
      });
    });
  }

  function init() {
    injectStyles();
    document.querySelectorAll("form.newsletter-form").forEach(wireNewsletter);
    document.querySelectorAll("form[data-lead-form]").forEach(wireLeadForm);
    wireTourQuoteTriggers();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
