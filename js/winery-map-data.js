/**
 * Shared winery map coordinates used by /plan-your-day and the homepage map.
 * Do NOT replace these with data-wineries.json lat/lng — those values are
 * inaccurate and place pins in the bay. Keep this file as the single source
 * of truth for interactive map markers.
 *
 * Coordinates verified against OpenStreetMap Nominatim where a winery POI
 * exists; remaining entries keep curated landfall positions.
 */
(function (global) {
  var W = [
    // OLD MISSION
    { id: "cgt", n: "Chateau Grand Traverse", p: "old-mission", lat: 44.86489, lng: -85.52002, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "cc", n: "Chateau Chantal", p: "old-mission", lat: 44.91964, lng: -85.50202, hrs: "11am–7pm", close: 19, open: 11 },
    { id: "pc", n: "Peninsula Cellars", p: "old-mission", lat: 44.8542, lng: -85.52737, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "be", n: "Brys Estate", p: "old-mission", lat: 44.88659, lng: -85.50987, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "2l", n: "2 Lads Winery", p: "old-mission", lat: 44.93434, lng: -85.4960, hrs: "12–6pm", close: 18, open: 12 },
    { id: "bh", n: "Bowers Harbor Vineyards", p: "old-mission", lat: 44.89145, lng: -85.51766, hrs: "10:30am–6pm", close: 18, open: 10.5 },
    { id: "hv", n: "Hawthorne Vineyards", p: "old-mission", lat: 44.82636, lng: -85.56104, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "lfc", n: "Left Foot Charley", p: "old-mission", lat: 44.75629, lng: -85.64522, hrs: "12–6pm", close: 18, open: 12 },
    { id: "mv", n: "Mari Vineyards", p: "old-mission", lat: 44.80853, lng: -85.56553, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "bn", n: "Bonobo Winery", p: "old-mission", lat: 44.86042, lng: -85.52337, hrs: "11am–7pm", close: 19, open: 11 },
    // LEELANAU
    { id: "bsf", n: "Black Star Farms", p: "leelanau", lat: 44.93268, lng: -85.6364, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "45n", n: "45 North Vineyard", p: "leelanau", lat: 45.0006, lng: -85.68311, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "lm", n: "L. Mawby", p: "leelanau", lat: 44.91379, lng: -85.65228, hrs: "12–5pm", close: 17, open: 12 },
    { id: "cic", n: "Ciccone Vineyard", p: "leelanau", lat: 44.925, lng: -85.665, hrs: "12–5pm", close: 17, open: 12 },
    { id: "gp", n: "Gill's Pier Winery", p: "leelanau", lat: 45.118, lng: -85.62, hrs: "12–5pm", close: 17, open: 12 },
    { id: "lc", n: "Leelanau Cellars", p: "leelanau", lat: 45.05523, lng: -85.58838, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "bl", n: "Bel Lago Vineyard", p: "leelanau", lat: 44.945, lng: -85.795, hrs: "12–5pm", close: 17, open: 12 },
    { id: "sl", n: "Shady Lane Cellars", p: "leelanau", lat: 44.89181, lng: -85.66247, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "vt", n: "Verterra Winery", p: "leelanau", lat: 45.02303, lng: -85.75952, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "bb", n: "Brengman Brothers", p: "leelanau", lat: 44.83649, lng: -85.66735, hrs: "11am–7pm", close: 19, open: 11 },
    { id: "rv", n: "Raftshol Vineyards", p: "leelanau", lat: 45.00869, lng: -85.61908, hrs: "12–6pm", close: 18, open: 12 },
    { id: "wv", n: "Willow Vineyards", p: "leelanau", lat: 44.93, lng: -85.668, hrs: "12–5pm", close: 17, open: 12 },
    { id: "gh", n: "Good Harbor Vineyards", p: "leelanau", lat: 44.975, lng: -85.715, hrs: "11am–5pm", close: 17, open: 11 },
  ];

  var WMap = {};
  W.forEach(function (w) {
    WMap[w.id] = w;
  });

  /** Same divIcon HTML used on /plan-your-day (minus itinerary number state). */
  function wineryIcon(w, actionLabel) {
    var cls = w.p === "old-mission" ? "om" : "ll";
    var action = actionLabel || "Click to filter tours";
    return L.divIcon({
      className: "",
      html:
        '<div class="winery-pin" data-id="' +
        w.id +
        '"><div class="pin-tooltip"><div class="tt-name">' +
        w.n +
        '</div><div class="tt-sub">' +
        w.hrs +
        '</div><div class="tt-action">' +
        action +
        '</div></div><div class="pin-dot ' +
        cls +
        '"></div></div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  }

  global.TCWT_WINERIES = W;
  global.TCWT_WINERY_MAP = WMap;
  global.TCWT_wineryIcon = wineryIcon;
})(window);
