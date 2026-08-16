(function () {
  const API = "/api/leads";

  function privacyHref() {
    const depth = window.location.pathname.replace(/\/+$/, "").split("/").filter(Boolean).length;
    const nested = depth > 1 || /\/(wineries|breweries|cideries|journal|admin)\//.test(window.location.pathname);
    return nested ? "../privacy.html" : "privacy.html";
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
      .lead-status[data-kind="ok"] { color:#2f6b3a; }
      .newsletter .lead-status[data-kind="ok"] { color:#D4BC8B; }
      .lead-status[data-kind="error"] { color:#9b2c2c; }
      .newsletter .lead-status[data-kind="error"] { color:#f3c1c1; }
    `;
    document.head.appendChild(style);
  }

  function init() {
    injectStyles();
    document.querySelectorAll("form.newsletter-form").forEach(wireNewsletter);
    document.querySelectorAll("form[data-lead-form]").forEach(wireLeadForm);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
