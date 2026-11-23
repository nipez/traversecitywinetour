/**
 * Shared winery map coordinates used by /plan-your-day and the homepage map.
 * Do NOT replace these with data-wineries.json lat/lng — those values are
 * inaccurate and place pins in the bay. Keep this file as the single source
 * of truth for interactive map markers.
 */
(function (global) {
  var W = [
    // OLD MISSION
    { id: "cgt", n: "Chateau Grand Traverse", p: "old-mission", lat: 44.8649, lng: -85.5198, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "cc", n: "Chateau Chantal", p: "old-mission", lat: 44.9195, lng: -85.5020, hrs: "11am–7pm", close: 19, open: 11 },
    { id: "pc", n: "Peninsula Cellars", p: "old-mission", lat: 44.8540, lng: -85.5272, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "be", n: "Brys Estate", p: "old-mission", lat: 44.8867, lng: -85.5098, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "2l", n: "2 Lads Winery", p: "old-mission", lat: 44.9342, lng: -85.4960, hrs: "12–6pm", close: 18, open: 12 },
    { id: "bh", n: "Bowers Harbor Vineyards", p: "old-mission", lat: 44.8410, lng: -85.5480, hrs: "10:30am–6pm", close: 18, open: 10.5 },
    { id: "hv", n: "Hawthorne Vineyards", p: "old-mission", lat: 44.8264, lng: -85.5611, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "lfc", n: "Left Foot Charley", p: "old-mission", lat: 44.7562, lng: -85.6452, hrs: "12–6pm", close: 18, open: 12 },
    { id: "mv", n: "Mari Vineyards", p: "old-mission", lat: 44.8085, lng: -85.5656, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "bn", n: "Bonobo Winery", p: "old-mission", lat: 44.8605, lng: -85.5232, hrs: "11am–7pm", close: 19, open: 11 },
    // LEELANAU
    { id: "bsf", n: "Black Star Farms", p: "leelanau", lat: 44.9780, lng: -85.6400, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "45n", n: "45 North Vineyard", p: "leelanau", lat: 44.9350, lng: -85.7400, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "lm", n: "L. Mawby", p: "leelanau", lat: 44.9560, lng: -85.7100, hrs: "12–5pm", close: 17, open: 12 },
    { id: "cic", n: "Ciccone Vineyard", p: "leelanau", lat: 44.9480, lng: -85.7050, hrs: "12–5pm", close: 17, open: 12 },
    { id: "gp", n: "Gill's Pier Winery", p: "leelanau", lat: 45.0600, lng: -85.6800, hrs: "12–5pm", close: 17, open: 12 },
    { id: "lc", n: "Leelanau Cellars", p: "leelanau", lat: 45.0150, lng: -85.6050, hrs: "10am–6pm", close: 18, open: 10 },
    { id: "bl", n: "Bel Lago Vineyard", p: "leelanau", lat: 44.8800, lng: -85.8500, hrs: "12–5pm", close: 17, open: 12 },
    { id: "sl", n: "Shady Lane Cellars", p: "leelanau", lat: 44.9620, lng: -85.6950, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "vt", n: "Verterra Winery", p: "leelanau", lat: 45.0230, lng: -85.7600, hrs: "11am–6pm", close: 18, open: 11 },
    { id: "bb", n: "Brengman Brothers", p: "leelanau", lat: 44.8200, lng: -85.6700, hrs: "11am–7pm", close: 19, open: 11 },
    { id: "rv", n: "Raftshol Vineyards", p: "leelanau", lat: 44.9900, lng: -85.6200, hrs: "12–6pm", close: 18, open: 12 },
    { id: "wv", n: "Willow Vineyards", p: "leelanau", lat: 44.9700, lng: -85.6800, hrs: "12–5pm", close: 17, open: 12 },
    { id: "gh", n: "Good Harbor Vineyards", p: "leelanau", lat: 44.9100, lng: -85.8200, hrs: "11am–5pm", close: 17, open: 11 },
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
