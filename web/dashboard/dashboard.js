let map;
let markerCluster;
let summary;
let activeOnlyFilter;
let airOnlyFilter;
let closedFilter;
let totalFacilities;
let activeFacilities;
let airEmissionSources;
let municipalities;
let currentBounds;

function syncMapSize() {
  if (!map) return;
  map.invalidateSize({ pan: false });
}

function fitCurrentBounds() {
  if (!map || !currentBounds || !currentBounds.isValid()) return;
  syncMapSize();
  map.fitBounds(currentBounds, {
    padding: [30, 30],
  });
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => {
    switch (char) {
      case "&": return "&amp;";
      case "<": return "&lt;";
      case ">": return "&gt;";
      case '"': return "&quot;";
      case "'": return "&#39;";
      default: return char;
    }
  });
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value || 0);
}

function statusLabel(properties) {
  return properties.operating_status || "unknown";
}

function isActive(properties) {
  return statusLabel(properties) === "active";
}

function hasAir(properties) {
  return properties.has_air_emissions === true || properties.har_utslipp_luft === 1;
}

function hasWater(properties) {
  return properties.has_water_emissions === true || properties.har_utslipp_vann === 1;
}

function markerStyle(properties) {
  if (!isActive(properties)) {
    return { color: "#6b7280", fillColor: "#9ca3af" };
  }
  if (hasAir(properties)) {
    return { color: "#991b1b", fillColor: "#dc2626" };
  }
  if (hasWater(properties)) {
    return { color: "#1d4ed8", fillColor: "#3b82f6" };
  }
  return { color: "#6b7280", fillColor: "#9ca3af" };
}

function popupHtml(properties) {
  const name = escapeHtml(properties.name || properties.navn || "Unknown facility");
  const operator = escapeHtml(properties.operator || properties.ansvarlig_enhet || "Unknown operator");
  const sector = escapeHtml(properties.sector_classification || properties.bransje || "Unknown sector");
  const municipality = escapeHtml(properties.municipality || properties.kommunenavn || "Unknown municipality");
  const reportYear = escapeHtml(properties.latest_reporting_year || properties.siste_rapportering_aar || "Unknown");
  const url = properties.reference_url || properties.faktaark;
  const link = url
    ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener">Norske Utslipp faktaark</a>`
    : "No faktaark link";

  return `
    <div class="popup">
      <h3>${name}</h3>
      <dl>
        <div><dt>Operator</dt><dd>${operator}</dd></div>
        <div><dt>Sector</dt><dd>${sector}</dd></div>
        <div><dt>Municipality</dt><dd>${municipality}</dd></div>
        <div><dt>Last report year</dt><dd>${reportYear}</dd></div>
        <div><dt>Source</dt><dd>${link}</dd></div>
      </dl>
    </div>
  `;
}

function updateKpis(features) {
  const props = features.map((feature) => feature.properties || {});
  totalFacilities.textContent = formatNumber(features.length);
  activeFacilities.textContent = formatNumber(props.filter(isActive).length);
  airEmissionSources.textContent = formatNumber(props.filter(hasAir).length);
  municipalities.textContent = formatNumber(
    new Set(props.map((item) => item.municipality || item.kommunenavn).filter(Boolean)).size,
  );
}

function renderMap(geojson) {
  const features = geojson.features || [];
  markerCluster.clearLayers();

  const mainlandLayer = L.featureGroup();
  for (const feature of features) {
    const geometry = feature.geometry || {};
    if (geometry.type !== "Point" || !Array.isArray(geometry.coordinates)) {
      continue;
    }

    const [longitude, latitude] = geometry.coordinates;
    const properties = feature.properties || {};
    const style = markerStyle(properties);
    const marker = L.circleMarker([latitude, longitude], {
      radius: 5,
      color: style.color,
      weight: 2,
      fillColor: style.fillColor,
      fillOpacity: 0.84,
    }).bindPopup(popupHtml(properties));

    markerCluster.addLayer(marker);
    if (latitude < 72) {
      mainlandLayer.addLayer(marker);
    }
  }

  updateKpis(features);
  summary.textContent = `${formatNumber(features.length)} facilities shown from Miljødirektoratet / Norske Utslipp.`;

  const layer = mainlandLayer.getLayers().length ? mainlandLayer : markerCluster;
  currentBounds = layer.getBounds();
  fitCurrentBounds();

  setTimeout(() => {
    fitCurrentBounds();
  }, 300);
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

async function loadMap() {
  const params = new URLSearchParams({
    active_only: activeOnlyFilter.checked ? "true" : "false",
    air_emissions_only: airOnlyFilter.checked ? "true" : "false",
    include_closed: closedFilter.checked ? "true" : "false",
  });
  const geojson = await fetchJson(`/api/raw/miljodirektoratet/industri_landbasert.geojson?${params}`);
  renderMap(geojson);
}

function queueLoad() {
  summary.textContent = "Loading Miljødirektoratet facility data...";
  loadMap().catch((error) => {
    summary.textContent = "Unable to load facility map data.";
    console.error(error);
  });
}

function initMap() {
  map = L.map("map", { worldCopyJump: true }).setView([62.5, 10.5], 5);
  const tileLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  tileLayer.on("load", () => {
    syncMapSize();
  });

  summary = document.querySelector("#summary");
  activeOnlyFilter = document.querySelector("#activeOnlyFilter");
  airOnlyFilter = document.querySelector("#airOnlyFilter");
  closedFilter = document.querySelector("#closedFilter");
  totalFacilities = document.querySelector("#totalFacilities");
  activeFacilities = document.querySelector("#activeFacilities");
  airEmissionSources = document.querySelector("#airEmissionSources");
  municipalities = document.querySelector("#municipalities");

  markerCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 42,
  });
  map.addLayer(markerCluster);

  setTimeout(() => {
    syncMapSize();
  }, 300);

  const mapPanel = document.querySelector(".map-panel");
  if ("ResizeObserver" in window && mapPanel) {
    const resizeObserver = new ResizeObserver(() => {
      syncMapSize();
    });
    resizeObserver.observe(mapPanel);
  }

  window.addEventListener("resize", syncMapSize);

  activeOnlyFilter.addEventListener("change", queueLoad);
  airOnlyFilter.addEventListener("change", queueLoad);
  closedFilter.addEventListener("change", queueLoad);

  queueLoad();
}

document.addEventListener("DOMContentLoaded", initMap);
