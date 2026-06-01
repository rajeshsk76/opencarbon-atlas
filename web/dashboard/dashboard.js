const map = L.map("map", { worldCopyJump: true }).setView([62.5, 10.5], 5);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

const summary = document.querySelector("#summary");
const totalEmissions = document.querySelector("#totalEmissions");
const plantCount = document.querySelector("#plantCount");
const markers = L.layerGroup().addTo(map);

function titleCase(value) {
  return String(value || "").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value || 0);
}

function formatKtCo2e(value) {
  return `${formatNumber((Number(value) || 0) / 1000)} ktCO2e/year`;
}

function markerRadius(emissions, maxEmissions) {
  if (!emissions || !maxEmissions) {
    return 8;
  }
  return 8 + Math.sqrt(emissions / maxEmissions) * 24;
}

function popupHtml(properties) {
  const emissions = formatKtCo2e(properties.emissions);
  return `
    <div class="popup">
      <div class="popup-title">${properties.name}</div>
      <div class="popup-meta">${titleCase(properties.sector)} · ${properties.operator}</div>
      <dl class="popup-facts">
        <div>
          <dt>Emissions</dt>
          <dd>${emissions}</dd>
        </div>
        <div>
          <dt>Capture</dt>
          <dd>${titleCase(properties.capture_status)}</dd>
        </div>
        <div>
          <dt>Data quality</dt>
          <dd>${properties.data_quality || "n/a"}</dd>
        </div>
        <div>
          <dt>Reference</dt>
          <dd>${properties.reference_id || "n/a"}</dd>
        </div>
      </dl>
    </div>
  `;
}

function renderMap(geojson) {
  const features = geojson.features || [];
  const maxEmissions = Math.max(...features.map((feature) => feature.properties.emissions || 0), 0);
  const bounds = [];

  for (const feature of features) {
    const [longitude, latitude] = feature.geometry.coordinates;
    const properties = feature.properties;
    const marker = L.circleMarker([latitude, longitude], {
      radius: markerRadius(properties.emissions, maxEmissions),
      color: "#0f5132",
      weight: 2,
      fillColor: "#198754",
      fillOpacity: 0.72,
    }).bindPopup(popupHtml(properties));
    marker.addTo(markers);
    bounds.push([latitude, longitude]);
  }

  const totalScope1 = features.reduce((total, feature) => total + (feature.properties.emissions || 0), 0);

  summary.textContent = `${features.length} plants with latest Scope 1 emissions, capture status, and A-E evidence quality.`;
  totalEmissions.textContent = formatKtCo2e(totalScope1);
  plantCount.textContent = formatNumber(features.length);

  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [32, 32], maxZoom: 7 });
  }
}

function chartOptions(unitLabel) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = formatNumber(context.parsed.y ?? context.parsed);
            return unitLabel ? `${context.dataset.label}: ${value} ${unitLabel}` : `${context.dataset.label}: ${value}`;
          },
        },
      },
    },
    scales: unitLabel
      ? {
          y: {
            beginAtZero: true,
            title: { display: true, text: unitLabel },
          },
        }
      : undefined,
  };
}

function renderBarChart(canvasId, labels, values, label, color, unitLabel) {
  new Chart(document.querySelector(canvasId), {
    type: "bar",
    data: {
      labels,
      datasets: [{ label, data: values, backgroundColor: color, borderRadius: 4 }],
    },
    options: chartOptions(unitLabel),
  });
}

function renderDoughnutChart(canvasId, labels, values, label, colors) {
  new Chart(document.querySelector(canvasId), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ label, data: values, backgroundColor: colors, borderWidth: 0 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
    },
  });
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

async function boot() {
  const [geojson, sectorData, captureData, qualityData] = await Promise.all([
    fetchJson("/geojson"),
    fetchJson("/analytics/sector-emissions"),
    fetchJson("/analytics/capture-status"),
    fetchJson("/analytics/data-quality"),
  ]);

  const sectorsByEmissions = [...sectorData].sort(
    (left, right) => right.total_scope1_co2e - left.total_scope1_co2e,
  );

  renderMap(geojson);
  renderBarChart(
    "#sectorChart",
    sectorsByEmissions.map((row) => titleCase(row.sector)),
    sectorsByEmissions.map((row) => row.total_scope1_co2e / 1000),
    "Scope 1 CO2e",
    "#198754",
    "ktCO2e/year",
  );
  renderBarChart(
    "#captureChart",
    captureData.map((row) => titleCase(row.capture_status)),
    captureData.map((row) => row.count),
    "Facilities",
    "#0d6efd",
    "facilities",
  );
  renderDoughnutChart(
    "#qualityChart",
    qualityData.map((row) => row.data_quality),
    qualityData.map((row) => row.count),
    "Rows",
    ["#198754", "#20c997", "#ffc107", "#fd7e14", "#dc3545"],
  );
}

boot().catch((error) => {
  summary.textContent = "Unable to load dashboard data.";
  console.error(error);
});
