const map = L.map("map", { worldCopyJump: true }).setView([62.5, 10.5], 5);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

const summary = document.querySelector("#summary");
const totalEmissions = document.querySelector("#totalEmissions");
const plantCount = document.querySelector("#plantCount");
const markers = L.layerGroup().addTo(map);

const EXPECTED_EMISSIONS_UNIT = "tCO2e";

const QUALITY_COLOR = {
  A: "#198754",
  B: "#20c997",
  C: "#ffc107",
  D: "#fd7e14",
  E: "#dc3545",
};
const QUALITY_FALLBACK_COLOR = "#adb5bd";

const CAPTURE_ORDER = [
  "none",
  "study",
  "screening",
  "pilot",
  "planned",
  "under-construction",
  "installed",
];

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

function titleCase(value) {
  return String(value || "").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value || 0);
}

function formatKtCo2e(value) {
  return `${formatNumber((Number(value) || 0) / 1000)} ktCO2e/year`;
}

function hasEmissions(properties) {
  const unitOk =
    !properties.emissions_unit || properties.emissions_unit === EXPECTED_EMISSIONS_UNIT;
  return properties.emissions != null && unitOk;
}

function markerRadius(emissions, maxEmissions) {
  if (!emissions || !maxEmissions) {
    return 8;
  }
  return 8 + Math.sqrt(emissions / maxEmissions) * 24;
}

function popupHtml(properties) {
  const name = escapeHtml(properties.name || "n/a");
  const sector = escapeHtml(titleCase(properties.sector) || "n/a");
  const operator = escapeHtml(properties.operator || "n/a");
  const emissions = hasEmissions(properties)
    ? escapeHtml(formatKtCo2e(properties.emissions))
    : "n/a";
  const capture = escapeHtml(titleCase(properties.capture_status) || "n/a");
  const quality = escapeHtml(properties.data_quality || "n/a");
  const reference = escapeHtml(properties.reference_id || "n/a");
  return `
    <div class="popup">
      <div class="popup-title">${name}</div>
      <div class="popup-meta">${sector} · ${operator}</div>
      <dl class="popup-facts">
        <div>
          <dt>Emissions</dt>
          <dd>${emissions}</dd>
        </div>
        <div>
          <dt>Capture</dt>
          <dd>${capture}</dd>
        </div>
        <div>
          <dt>Data quality</dt>
          <dd>${quality}</dd>
        </div>
        <div>
          <dt>Reference</dt>
          <dd>${reference}</dd>
        </div>
      </dl>
    </div>
  `;
}

function renderMap(geojson) {
  const features = geojson.features || [];

  for (const feature of features) {
    const properties = feature.properties;
    if (properties.emissions_unit && properties.emissions_unit !== EXPECTED_EMISSIONS_UNIT) {
      console.warn(
        `Unexpected emissions_unit "${properties.emissions_unit}" for ${properties.name}; treating as no-data.`,
      );
    }
  }

  const reportedEmissions = features
    .filter((feature) => hasEmissions(feature.properties))
    .map((feature) => feature.properties.emissions);
  const maxEmissions = reportedEmissions.length ? Math.max(...reportedEmissions) : 0;
  const bounds = [];

  for (const feature of features) {
    const [longitude, latitude] = feature.geometry.coordinates;
    const properties = feature.properties;
    const reported = hasEmissions(properties);
    const marker = L.circleMarker([latitude, longitude], {
      radius: reported ? markerRadius(properties.emissions, maxEmissions) : 6,
      color: reported ? "#0f5132" : "#6c757d",
      weight: 2,
      fillColor: reported ? "#198754" : "#ffffff",
      fillOpacity: reported ? 0.72 : 0.5,
      dashArray: reported ? null : "3,3",
    }).bindPopup(popupHtml(properties));
    marker.addTo(markers);
    bounds.push([latitude, longitude]);
  }

  const totalScope1 = reportedEmissions.reduce((total, value) => total + value, 0);
  const reportedCount = reportedEmissions.length;

  summary.textContent = `${features.length} plants, ${reportedCount} with reported Scope 1 emissions and A-E evidence quality.`;
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

function renderSectorChart(sectorData) {
  const sorted = [...sectorData].sort(
    (left, right) => right.total_scope1_co2e - left.total_scope1_co2e,
  );
  renderBarChart(
    "#sectorChart",
    sorted.map((row) => titleCase(row.sector)),
    sorted.map((row) => row.total_scope1_co2e / 1000),
    "Scope 1 CO2e",
    "#198754",
    "ktCO2e/year",
  );
}

function renderCaptureChart(captureData) {
  const orderIndex = (status) => {
    const index = CAPTURE_ORDER.indexOf(status);
    return index === -1 ? CAPTURE_ORDER.length : index;
  };
  const sorted = [...captureData].sort(
    (left, right) => orderIndex(left.capture_status) - orderIndex(right.capture_status),
  );
  renderBarChart(
    "#captureChart",
    sorted.map((row) => titleCase(row.capture_status)),
    sorted.map((row) => row.count),
    "Facilities",
    "#0d6efd",
    "facilities",
  );
}

function renderQualityChart(qualityData) {
  renderDoughnutChart(
    "#qualityChart",
    qualityData.map((row) => row.data_quality),
    qualityData.map((row) => row.count),
    "Rows",
    qualityData.map((row) => QUALITY_COLOR[row.data_quality] || QUALITY_FALLBACK_COLOR),
  );
}

function showPanelError(canvasId, message) {
  const canvas = document.querySelector(canvasId);
  if (!canvas) return;
  const panel = canvas.closest(".chart-panel");
  if (!panel) return;
  canvas.remove();
  const note = document.createElement("p");
  note.className = "panel-error";
  note.textContent = message;
  panel.appendChild(note);
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("json")) {
    throw new Error(`${path} returned non-JSON content-type "${contentType}"`);
  }
  return response.json();
}

async function boot() {
  const sources = [
    { key: "geojson", path: "/geojson" },
    { key: "sector", path: "/analytics/sector-emissions" },
    { key: "capture", path: "/analytics/capture-status" },
    { key: "quality", path: "/analytics/data-quality" },
  ];

  const results = await Promise.allSettled(sources.map((source) => fetchJson(source.path)));
  const data = {};
  results.forEach((result, index) => {
    const { key, path } = sources[index];
    if (result.status === "fulfilled") {
      data[key] = result.value;
    } else {
      console.error(`Failed to load ${path}:`, result.reason);
    }
  });

  if (data.geojson) {
    renderMap(data.geojson);
  } else {
    summary.textContent = "Map data unavailable. Other panels may still render.";
  }

  if (data.sector) {
    renderSectorChart(data.sector);
  } else {
    showPanelError("#sectorChart", "Sector data unavailable.");
  }

  if (data.capture) {
    renderCaptureChart(data.capture);
  } else {
    showPanelError("#captureChart", "Capture status unavailable.");
  }

  if (data.quality) {
    renderQualityChart(data.quality);
  } else {
    showPanelError("#qualityChart", "Data quality unavailable.");
  }
}

boot().catch((error) => {
  summary.textContent = "Unable to load dashboard data.";
  console.error(error);
});
