/**
 * Extra Plan Your Day stops for venue detail pages that are not on the
 * curated homepage map (js/winery-map-data.js).
 *
 * Loaded only by /plan-your-day. Deep links use ?stops=<slug> (or short id).
 * Coordinates are geocoded to the tasting-room street address (or the live
 * tasting-room location when the detail-page address is outdated). Hours
 * mirror the Nov 2025 winter listings on each venue page. Do not merge
 * these into the homepage map.
 */
(function (global) {
  var EXTRA = [
    // Unmapped winery detail pages
    { id: "tabone-vineyards", slug: "tabone-vineyards", n: "Tabone Vineyards", p: "old-mission", kind: "winery", lat: 44.904596, lng: -85.514392, hrs: "Mon 12–5pm · Thu 12–5pm · Fri 11am–5pm · Sat 11am–5pm · Sun 12–5pm", close: 17, open: 11 },
    { id: "aurora-cellars", slug: "aurora-cellars", n: "Aurora Cellars", p: "leelanau", kind: "winery", lat: 45.015071, lng: -85.697599, hrs: "Mon–Fri 12–6pm · Sat–Sun 12–7pm", close: 19, open: 12 },
    { id: "blustone-vineyards", slug: "blustone-vineyards", n: "Blustone Vineyards", p: "leelanau", kind: "winery", lat: 44.993732, lng: -85.692426, hrs: "Thu–Fri 12–5pm · Sat 12–6pm · Sun–Mon 12–5pm", close: 18, open: 12 },
    { id: "boathouse-vineyards", slug: "boathouse-vineyards", n: "Boathouse Vineyards", p: "leelanau", kind: "winery", lat: 44.981167, lng: -85.713461, hrs: "Sun–Thu 12–5pm · Fri–Sat 12–6pm", close: 18, open: 12 },
    { id: "rove-estate", slug: "rove-estate", n: "Rove Estate", p: "leelanau", kind: "winery", lat: 44.77835, lng: -85.716996, hrs: "Mon–Thu 12–6pm · Fri–Sat 12–7pm · Sun 12–5pm", close: 19, open: 12 },
    { id: "chateau-fontaine", slug: "chateau-fontaine", n: "Chateau Fontaine", p: "leelanau", kind: "winery", lat: 44.947521, lng: -85.755196, hrs: "Daily 12–5pm", close: 17, open: 12 },
    { id: "silver-leaf-vineyard", slug: "silver-leaf-vineyard", n: "Silver Leaf Vineyard & Winery", p: "leelanau", kind: "winery", lat: 45.024356, lng: -85.62881, hrs: "Call ahead", close: 17, open: 11 },
    { id: "chateau-de-leelanau", slug: "chateau-de-leelanau", n: "Chateau de Leelanau", p: "leelanau", kind: "winery", lat: 44.906517, lng: -85.632344, hrs: "Call ahead", close: 17, open: 11 },
    { id: "good-neighbor-organic", slug: "good-neighbor-organic", n: "Good Neighbor Organic Winery", p: "leelanau", kind: "winery", lat: 45.105946, lng: -85.645254, hrs: "Call ahead", close: 17, open: 11 },
    { id: "longview-winery", slug: "longview-winery", n: "Longview Winery", p: "leelanau", kind: "winery", lat: 44.85314, lng: -85.793121, hrs: "Call ahead", close: 17, open: 11 },
    { id: "laurentide-winery", slug: "laurentide-winery", n: "Laurentide Winery", p: "leelanau", kind: "winery", lat: 44.981373, lng: -85.735603, hrs: "Fri–Tue 12–5pm", close: 17, open: 12 },

    // Cideries
    { id: "tandem-ciders", slug: "tandem-ciders", n: "Tandem Ciders", p: "leelanau", kind: "cidery", lat: 44.9542, lng: -85.6387, hrs: "Thu–Sun 12–6pm (seasonal hours vary)", close: 18, open: 12 },
    { id: "suttons-bay-ciders", slug: "suttons-bay-ciders", n: "Suttons Bay Ciders", p: "leelanau", kind: "cidery", lat: 44.9701, lng: -85.6452, hrs: "Daily 12–8pm (seasonal hours vary)", close: 20, open: 12 },
    { id: "taproot-cider-house", slug: "taproot-cider-house", n: "Taproot Cider House", p: "old-mission", kind: "cidery", lat: 44.764, lng: -85.6206, hrs: "Mon–Thu 3–10pm · Fri 12–11pm · Sat 11am–11pm · Sun 11am–9pm", close: 23, open: 11 },
    { id: "northern-natural-cider-house", slug: "northern-natural-cider-house", n: "Northern Natural Cider House", p: "old-mission", kind: "cidery", lat: 44.7645, lng: -85.6198, hrs: "Mon–Sat 12–8pm · Sun 12–6pm", close: 20, open: 12 },
    { id: "bel-lago-cidery", slug: "bel-lago-cidery", n: "Bel Lago Winery & Cidery", p: "leelanau", kind: "cidery", lat: 44.945, lng: -85.795, hrs: "Daily 11am–6pm (seasonal hours vary)", close: 18, open: 11 },
    { id: "left-foot-charley-cider", slug: "left-foot-charley-cider", n: "Left Foot Charley Cider", p: "old-mission", kind: "cidery", lat: 44.75629, lng: -85.64522, hrs: "Mon–Thu 12–7pm · Fri–Sat 12–8pm · Sun 12–6pm", close: 20, open: 12 },

    // Breweries
    { id: "rare-bird-brewpub", slug: "rare-bird-brewpub", n: "Rare Bird Brewpub", p: "old-mission", kind: "brewery", lat: 44.7648, lng: -85.6225, hrs: "Mon–Thu 3–11pm · Fri 12–12am · Sat 11am–12am · Sun 11am–10pm", close: 24, open: 11 },
    { id: "right-brain-brewery", slug: "right-brain-brewery", n: "Right Brain Brewery", p: "old-mission", kind: "brewery", lat: 44.7508, lng: -85.6112, hrs: "Mon–Thu 3–11pm · Fri 12–12am · Sat 12–12am · Sun 12–10pm", close: 24, open: 12 },
    { id: "workshop-brewing-company", slug: "workshop-brewing-company", n: "The Workshop Brewing Company", p: "old-mission", kind: "brewery", lat: 44.7618, lng: -85.6244, hrs: "Mon–Thu 3–11pm · Fri 12–12am · Sat 12–12am · Sun 12–10pm", close: 24, open: 12 },
    { id: "filling-station-microbrewery", slug: "filling-station-microbrewery", n: "The Filling Station Microbrewery", p: "old-mission", kind: "brewery", lat: 44.7524, lng: -85.6098, hrs: "Mon–Thu 11am–11pm · Fri–Sat 11am–12am · Sun 10am–10pm", close: 24, open: 10 },
    { id: "north-peak-brewing", slug: "north-peak-brewing", n: "North Peak Brewing Company", p: "old-mission", kind: "brewery", lat: 44.7658, lng: -85.6271, hrs: "Sun–Thu 11:30am–10pm · Fri–Sat 11:30am–11pm", close: 23, open: 11.5 },
    { id: "middlecoast-brewing", slug: "middlecoast-brewing", n: "Middle Coast Brewing", p: "old-mission", kind: "brewery", lat: 44.7635, lng: -85.6195, hrs: "Mon–Thu 3–10pm · Fri 12–11pm · Sat 11am–11pm · Sun 11am–9pm", close: 23, open: 11 },
    { id: "brewery-ferment", slug: "brewery-ferment", n: "Brewery Ferment", p: "old-mission", kind: "brewery", lat: 44.7712, lng: -85.6148, hrs: "Tue–Thu 3–9pm · Fri 2–10pm · Sat 12–10pm · Sun 12–7pm", close: 22, open: 12 },
    { id: "brewery-terra-firma", slug: "brewery-terra-firma", n: "Brewery Terra Firma", p: "old-mission", kind: "brewery", lat: 44.7441, lng: -85.5892, hrs: "Mon 12–8pm · Tue–Sat 12–10pm · Sun 12–9pm", close: 22, open: 12 },
    { id: "earthen-ales", slug: "earthen-ales", n: "Earthen Ales", p: "old-mission", kind: "brewery", lat: 44.7561, lng: -85.6093, hrs: "Daily 12–9pm (hours vary by location)", close: 21, open: 12 },
    { id: "hop-lot-brewing", slug: "hop-lot-brewing", n: "Hop Lot Brewing", p: "leelanau", kind: "brewery", lat: 44.9498, lng: -85.6441, hrs: "Mon–Sat 12–9pm · Sun 12–8pm", close: 21, open: 12 },
    { id: "jolly-pumpkin", slug: "jolly-pumpkin", n: "Jolly Pumpkin", p: "old-mission", kind: "brewery", lat: 44.8102, lng: -85.4981, hrs: "Sun–Thu 11:30am–9pm · Fri–Sat 11:30am–10pm", close: 22, open: 11.5 },
    { id: "lake-ann-brewing", slug: "lake-ann-brewing", n: "Lake Ann Brewing", p: "leelanau", kind: "brewery", lat: 44.7263, lng: -85.8492, hrs: "Thu–Fri 3–9pm · Sat 12–9pm · Sun 12–6pm", close: 21, open: 12 },
    { id: "silver-spruce-brewing", slug: "silver-spruce-brewing", n: "Silver Spruce Brewing Company", p: "old-mission", kind: "brewery", lat: 44.7558, lng: -85.6078, hrs: "Daily 12–9pm (hours vary by location)", close: 21, open: 12 },
    { id: "shorts-brewing-bellaire", slug: "shorts-brewing-bellaire", n: "Short's Brewing — Bellaire Pub", p: "leelanau", kind: "brewery", lat: 44.9779, lng: -85.2012, hrs: "Sun–Thu 11am–10pm · Fri–Sat 11am–11pm", close: 23, open: 11 },
    { id: "shorts-brewing-elk-rapids", slug: "shorts-brewing-elk-rapids", n: "Short's Brewing — Elk Rapids Pull Barn", p: "old-mission", kind: "brewery", lat: 44.9998, lng: -85.4152, hrs: "Mon–Thu 2–8pm · Fri 11am–9pm · Sat–Sun 11am–8pm", close: 21, open: 11 }
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
