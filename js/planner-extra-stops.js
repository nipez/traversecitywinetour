/**
 * Extra Plan Your Day stops for venue detail pages that are not on the
 * curated homepage map (js/winery-map-data.js).
 *
 * Loaded only by /plan-your-day. Deep links use ?stops=<slug> (or short id).
 * Coordinates for unmapped wineries are approximate landfall positions so
 * pins stay on land; drive times between extras fall back to the planner's
 * default estimate. Do not merge these into the homepage map.
 */
(function (global) {
  var EXTRA = [
    // Unmapped winery detail pages (approximate landfall near peninsula clusters)
    { id: "tabone-vineyards", slug: "tabone-vineyards", n: "Tabone Vineyards", p: "old-mission", kind: "winery", lat: 44.875, lng: -85.515, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "aurora-cellars", slug: "aurora-cellars", n: "Aurora Cellars", p: "leelanau", kind: "winery", lat: 45.02, lng: -85.75, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "blustone-vineyards", slug: "blustone-vineyards", n: "Blustone Vineyards", p: "leelanau", kind: "winery", lat: 45.05, lng: -85.74, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "boathouse-vineyards", slug: "boathouse-vineyards", n: "Boathouse Vineyards", p: "leelanau", kind: "winery", lat: 44.96, lng: -85.72, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "rove-estate", slug: "rove-estate", n: "Rove Estate", p: "leelanau", kind: "winery", lat: 44.97, lng: -85.70, hrs: "Call ahead", close: 18, open: 12, approx: true },
    { id: "chateau-fontaine", slug: "chateau-fontaine", n: "Chateau Fontaine", p: "leelanau", kind: "winery", lat: 44.98, lng: -85.71, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "silver-leaf-vineyard", slug: "silver-leaf-vineyard", n: "Silver Leaf Vineyard & Winery", p: "leelanau", kind: "winery", lat: 44.98, lng: -85.72, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "chateau-de-leelanau", slug: "chateau-de-leelanau", n: "Chateau de Leelanau", p: "leelanau", kind: "winery", lat: 44.96, lng: -85.73, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "good-neighbor-organic", slug: "good-neighbor-organic", n: "Good Neighbor Organic Winery", p: "leelanau", kind: "winery", lat: 45.01, lng: -85.70, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "longview-winery", slug: "longview-winery", n: "Longview Winery", p: "leelanau", kind: "winery", lat: 45.08, lng: -85.78, hrs: "Call ahead", close: 17, open: 11, approx: true },
    { id: "laurentide-winery", slug: "laurentide-winery", n: "Laurentide Winery", p: "leelanau", kind: "winery", lat: 45.09, lng: -85.80, hrs: "Call ahead", close: 17, open: 11, approx: true },

    // Cideries
    { id: "tandem-ciders", slug: "tandem-ciders", n: "Tandem Ciders", p: "leelanau", kind: "cidery", lat: 44.9542, lng: -85.6387, hrs: "Call ahead", close: 18, open: 12 },
    { id: "suttons-bay-ciders", slug: "suttons-bay-ciders", n: "Suttons Bay Ciders", p: "leelanau", kind: "cidery", lat: 44.9701, lng: -85.6452, hrs: "Call ahead", close: 18, open: 12 },
    { id: "taproot-cider-house", slug: "taproot-cider-house", n: "Taproot Cider House", p: "old-mission", kind: "cidery", lat: 44.764, lng: -85.6206, hrs: "Call ahead", close: 21, open: 12 },
    { id: "northern-natural-cider-house", slug: "northern-natural-cider-house", n: "Northern Natural Cider House", p: "old-mission", kind: "cidery", lat: 44.7645, lng: -85.6198, hrs: "Call ahead", close: 21, open: 12 },
    { id: "bel-lago-cidery", slug: "bel-lago-cidery", n: "Bel Lago Winery & Cidery", p: "leelanau", kind: "cidery", lat: 44.945, lng: -85.795, hrs: "Call ahead", close: 17, open: 12 },
    { id: "left-foot-charley-cider", slug: "left-foot-charley-cider", n: "Left Foot Charley Cider", p: "old-mission", kind: "cidery", lat: 44.75629, lng: -85.64522, hrs: "Call ahead", close: 18, open: 12 },

    // Breweries
    { id: "rare-bird-brewpub", slug: "rare-bird-brewpub", n: "Rare Bird Brewpub", p: "old-mission", kind: "brewery", lat: 44.7648, lng: -85.6225, hrs: "Call ahead", close: 22, open: 12 },
    { id: "right-brain-brewery", slug: "right-brain-brewery", n: "Right Brain Brewery", p: "old-mission", kind: "brewery", lat: 44.7508, lng: -85.6112, hrs: "Call ahead", close: 22, open: 12 },
    { id: "workshop-brewing-company", slug: "workshop-brewing-company", n: "The Workshop Brewing Company", p: "old-mission", kind: "brewery", lat: 44.7618, lng: -85.6244, hrs: "Call ahead", close: 22, open: 12 },
    { id: "filling-station-microbrewery", slug: "filling-station-microbrewery", n: "The Filling Station Microbrewery", p: "old-mission", kind: "brewery", lat: 44.7524, lng: -85.6098, hrs: "Call ahead", close: 22, open: 12 },
    { id: "north-peak-brewing", slug: "north-peak-brewing", n: "North Peak Brewing Company", p: "old-mission", kind: "brewery", lat: 44.7658, lng: -85.6271, hrs: "Call ahead", close: 22, open: 12 },
    { id: "middlecoast-brewing", slug: "middlecoast-brewing", n: "Middle Coast Brewing", p: "old-mission", kind: "brewery", lat: 44.7635, lng: -85.6195, hrs: "Call ahead", close: 22, open: 12 },
    { id: "brewery-ferment", slug: "brewery-ferment", n: "Brewery Ferment", p: "old-mission", kind: "brewery", lat: 44.7712, lng: -85.6148, hrs: "Call ahead", close: 22, open: 12 },
    { id: "brewery-terra-firma", slug: "brewery-terra-firma", n: "Brewery Terra Firma", p: "old-mission", kind: "brewery", lat: 44.7441, lng: -85.5892, hrs: "Call ahead", close: 22, open: 12 },
    { id: "earthen-ales", slug: "earthen-ales", n: "Earthen Ales", p: "old-mission", kind: "brewery", lat: 44.7561, lng: -85.6093, hrs: "Call ahead", close: 22, open: 12 },
    { id: "hop-lot-brewing", slug: "hop-lot-brewing", n: "Hop Lot Brewing", p: "leelanau", kind: "brewery", lat: 44.9498, lng: -85.6441, hrs: "Call ahead", close: 21, open: 12 },
    { id: "jolly-pumpkin", slug: "jolly-pumpkin", n: "Jolly Pumpkin", p: "old-mission", kind: "brewery", lat: 44.8102, lng: -85.4981, hrs: "Call ahead", close: 21, open: 11 },
    { id: "lake-ann-brewing", slug: "lake-ann-brewing", n: "Lake Ann Brewing", p: "leelanau", kind: "brewery", lat: 44.7263, lng: -85.8492, hrs: "Call ahead", close: 21, open: 12 },
    { id: "silver-spruce-brewing", slug: "silver-spruce-brewing", n: "Silver Spruce Brewing Company", p: "old-mission", kind: "brewery", lat: 44.7558, lng: -85.6078, hrs: "Call ahead", close: 22, open: 12 },
    { id: "shorts-brewing-bellaire", slug: "shorts-brewing-bellaire", n: "Short's Brewing — Bellaire Pub", p: "leelanau", kind: "brewery", lat: 44.9779, lng: -85.2012, hrs: "Call ahead", close: 22, open: 11 },
    { id: "shorts-brewing-elk-rapids", slug: "shorts-brewing-elk-rapids", n: "Short's Brewing — Elk Rapids Pull Barn", p: "old-mission", kind: "brewery", lat: 44.9998, lng: -85.4152, hrs: "Call ahead", close: 22, open: 11 },
  ];

  function mergePlannerExtras(wineryList, wineryMap, bySlug) {
    EXTRA.forEach(function (stop) {
      if (wineryMap[stop.id]) return;
      wineryList.push(stop);
      wineryMap[stop.id] = stop;
      if (stop.slug && bySlug) bySlug[stop.slug] = stop;
    });
  }

  function resolveStopToken(token, wineryMap, bySlug) {
    if (!token) return null;
    var t = String(token).trim();
    if (!t) return null;
    if (wineryMap && wineryMap[t]) return t;
    if (bySlug && bySlug[t]) return bySlug[t].id;
    if (global.TCWT_resolveStopToken) {
      var core = global.TCWT_resolveStopToken(t);
      if (core) return core;
    }
    return null;
  }

  global.TCWT_PLANNER_EXTRA_STOPS = EXTRA;
  global.TCWT_mergePlannerExtras = mergePlannerExtras;
  global.TCWT_resolvePlannerStop = resolveStopToken;
})(window);
