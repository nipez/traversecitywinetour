/**
 * Affiliate partner IDs — single config spot for Viator / GetYourGuide.
 * Replace the TODO placeholders with Nick's live IDs when ready.
 * Links work without an ID (OTA pages still open); the query param is only
 * appended when the placeholder has been replaced.
 */
(function (global) {
  // *** AFFILIATE IDS — set once here ***
  var VIATOR_PID = "VIATOR_PID_TODO"; // e.g. P00012345
  var GYG_PARTNER_ID = "GYG_PARTNER_ID_TODO"; // e.g. ABC123XY

  function isPlaceholder(value, todoToken) {
    return !value || value === todoToken || value.indexOf("_TODO") !== -1;
  }

  function appendParam(url, key, value) {
    if (!url || isPlaceholder(value, key === "pid" ? "VIATOR_PID_TODO" : "GYG_PARTNER_ID_TODO")) {
      return url;
    }
    var sep = url.indexOf("?") >= 0 ? "&" : "?";
    return url + sep + encodeURIComponent(key) + "=" + encodeURIComponent(value);
  }

  function buildViatorUrl(baseUrl) {
    var url = appendParam(baseUrl, "pid", VIATOR_PID);
    if (!isPlaceholder(VIATOR_PID, "VIATOR_PID_TODO")) {
      url = appendParam(url, "medium", "link");
      url = appendParam(url, "campaign", "traversecitywinetour");
    }
    return url;
  }

  function buildGygUrl(baseUrl) {
    return appendParam(baseUrl, "partner_id", GYG_PARTNER_ID);
  }

  function wireAffiliateLinks() {
    document.querySelectorAll("[data-affiliate-viator]").forEach(function (el) {
      var base = el.getAttribute("data-affiliate-viator");
      if (!base) return;
      el.setAttribute("href", buildViatorUrl(base));
      el.setAttribute("rel", "sponsored nofollow noopener");
      el.setAttribute("target", "_blank");
    });
    document.querySelectorAll("[data-affiliate-gyg]").forEach(function (el) {
      var base = el.getAttribute("data-affiliate-gyg");
      if (!base) return;
      el.setAttribute("href", buildGygUrl(base));
      el.setAttribute("rel", "sponsored nofollow noopener");
      el.setAttribute("target", "_blank");
    });
  }

  global.TCWT_AFFILIATE = {
    VIATOR_PID: VIATOR_PID,
    GYG_PARTNER_ID: GYG_PARTNER_ID,
    buildViatorUrl: buildViatorUrl,
    buildGygUrl: buildGygUrl,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wireAffiliateLinks);
  } else {
    wireAffiliateLinks();
  }
})(window);
