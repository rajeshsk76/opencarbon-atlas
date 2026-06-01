const map = L.map("map", { worldCopyJump: true }).setView([64.5, 11], 5);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

const countyFilter = document.querySelector("#countyFilter");
const sectorFilter = document.querySelector("#sectorFilter");
const plantList = document.querySelector("#plantList");
const summary = document.querySelector("#summary");
const markers = L.layerGroup().addTo(map);

const state = {
  features: [],
};

function titleCase(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function fillSelect(select, values) {
  for (const value of [...new Set(values)].sort()) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = titleCase(value);
    select.append(option);
  }
}

function filteredFeatures() {
  return state.features.filter((feature) => {
    const properties = feature.properties;
    return (!countyFilter.value || properties.county === countyFilter.value)
      && (!sectorFilter.value || properties.sector === sectorFilter.value);
  });
}

function popupHtml(properties) {
  return `
    <div class="popup-title">${properties.name}</div>
    <div class="popup-meta">${properties.operator} · ${properties.municipality}, ${properties.county}</div>
    <div>${titleCase(properties.sector)} · ${titleCase(properties.status)}</div>
    <div>${properties.primary_product}</div>
  `;
}

function render() {
  markers.clearLayers();
  plantList.replaceChildren();

  const features = filteredFeatures();
  const bounds = [];

  for (const feature of features) {
    const [longitude, latitude] = feature.geometry.coordinates;
    const properties = feature.properties;
    const marker = L.circleMarker([latitude, longitude], {
      radius: 8,
      color: "#0b5f59",
      weight: 2,
      fillColor: "#0f766e",
      fillOpacity: 0.85,
    }).bindPopup(popupHtml(properties));
    marker.addTo(markers);
    bounds.push([latitude, longitude]);

    const card = document.createElement("button");
    card.className = "plant-card";
    card.type = "button";
    card.innerHTML = `
      <strong>${properties.name}</strong>
      <span>${properties.operator} · ${properties.county}</span>
      <span>${titleCase(properties.sector)}</span>
      <span class="badge">${titleCase(properties.status)}</span>
    `;
    card.addEventListener("click", () => {
      map.setView([latitude, longitude], 8);
      marker.openPopup();
    });
    plantList.append(card);
  }

  summary.textContent = `${features.length} facilities shown`;

  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [30, 30], maxZoom: 7 });
  }
}

async function boot() {
  const response = await fetch("/api/locations.geojson");
  const geojson = await response.json();
  state.features = geojson.features;
  fillSelect(countyFilter, state.features.map((feature) => feature.properties.county));
  fillSelect(sectorFilter, state.features.map((feature) => feature.properties.sector));
  countyFilter.addEventListener("change", render);
  sectorFilter.addEventListener("change", render);
  render();
}

boot().catch((error) => {
  summary.textContent = "Unable to load map data.";
  console.error(error);
});

