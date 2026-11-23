/**
 * Shared Leaflet basemap for Traverse City Wine Tour.
 * CARTO free CDN tiles now require an API key (they return watermark PNGs).
 * Esri Light Gray Canvas needs no key and matches our cream/burgundy UI.
 */
(function (global) {
  var TILE_URL =
    "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}";
  var ATTRIBUTION =
    'Tiles &copy; <a href="https://www.esri.com/">Esri</a> &mdash; Esri, HERE, Garmin, FAO, NOAA, USGS';
  var MAX_ZOOM = 16;

  function addBasemap(map) {
    return L.tileLayer(TILE_URL, {
      attribution: ATTRIBUTION,
      maxZoom: MAX_ZOOM,
    }).addTo(map);
  }

  global.TCWT_MAP = {
    TILE_URL: TILE_URL,
    ATTRIBUTION: ATTRIBUTION,
    MAX_ZOOM: MAX_ZOOM,
    addBasemap: addBasemap,
  };
})(window);
