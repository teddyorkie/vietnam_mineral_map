window.MineralMap = (() => {
  let map = null;
  let geojsonLayer = null;
  let tileLayer = null;
  let tilesEnabled = false;
  let islandMarkers = [];
  let layersById = {};
  let summaryById = {};
  let selectedId = null;
  let activeFilters = { group: "", mineral_id: "", metric_type: "", q: "" };
  let onSelectCallback = null;

  const VIETNAM_CENTER = [16.1, 106.6];
  const VIETNAM_ZOOM = 6;

  function init(containerId, geojsonData, onSelect) {
    onSelectCallback = onSelect;
    map = L.map(containerId, {
      center: VIETNAM_CENTER,
      zoom: VIETNAM_ZOOM,
      minZoom: 5,
      maxZoom: 12,
      zoomControl: true,
      preferCanvas: false,
    });

    tileLayer = L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      {
        attribution: "&copy; OpenStreetMap &copy; CARTO",
        subdomains: "abcd",
        maxZoom: 19,
      }
    );

    geojsonLayer = L.geoJSON(geojsonData, {
      style: (feature) => styleForFeature(feature),
      onEachFeature: (feature, layer) => {
        const pid = feature.properties.province_id;
        layersById[pid] = layer;

        layer.on({
          mouseover: (e) => {
            const target = e.target;
            target.setStyle({
              weight: 2.4,
              color: "#0f172a",
              fillOpacity: 0.92,
            });
            target.bringToFront();
            updateTooltipContent(pid, target);
          },
          mouseout: (e) => {
            geojsonLayer.resetStyle(e.target);
            if (selectedId && layersById[selectedId]) {
              applySelectedStyle(layersById[selectedId]);
            }
          },
          click: () => {
            selectProvince(pid, true);
            if (onSelectCallback) onSelectCallback(pid);
          },
        });
      },
    }).addTo(map);

    addIslandMarkers();
    fitVietnam();
    renderLegend();
  }

  function addIslandMarkers() {
    islandMarkers.forEach((m) => m.remove());
    islandMarkers = [];

    const islands = [
      { coords: [16.5, 112.0], key: "hoang_sa", provinceId: "48" },
      { coords: [10.0, 114.2], key: "truong_sa", provinceId: "56" },
    ];

    islands.forEach((isl) => {
      const icon = L.divIcon({
        className: "island-marker-wrap",
        html: `<div class="island-label">${window.I18n.t(isl.key)}</div>`,
        iconSize: null,
      });
      const marker = L.marker(isl.coords, { icon, interactive: true }).addTo(map);
      marker.on("click", () => {
        if (onSelectCallback) onSelectCallback(isl.provinceId);
      });
      islandMarkers.push(marker);
    });
  }

  function getPalette() {
    if (activeFilters.group === "Năng lượng") {
      return { low: "#fcd34d", high: "#d97706", border: "#b45309" };
    }
    if (activeFilters.group === "Kim loại") {
      return { low: "#60a5fa", high: "#2563eb", border: "#1d4ed8" };
    }
    if (activeFilters.group === "Phi kim loại") {
      return { low: "#34d399", high: "#059669", border: "#047857" };
    }
    return { low: "#38bdf8", high: "#0369a1", border: "#075985" };
  }

  function styleForFeature(feature) {
    const pid = feature.properties.province_id;
    const info = summaryById[pid];
    const palette = getPalette();
    const isFiltering = Boolean(
      activeFilters.group || activeFilters.mineral_id || activeFilters.metric_type || activeFilters.q
    );

    let fillColor = "#e2e8f0";
    let fillOpacity = 0.72;
    let color = "#94a3b8";
    let weight = 1;

    if (info && info.has_match) {
      if (isFiltering && info.distinct_mineral_count === 0) {
        // Matched via province name / legacy merged_from search without minerals
        fillColor = "#a5f3fc";
        fillOpacity = 0.82;
        color = "#0891b2";
        weight = 1.6;
      } else if (info.distinct_mineral_count >= 2) {
        fillColor = palette.high;
        fillOpacity = 0.88;
        color = "#ffffff";
        weight = 1.3;
      } else if (info.distinct_mineral_count === 1) {
        fillColor = palette.low;
        fillOpacity = 0.82;
        color = "#ffffff";
        weight = 1.2;
      }
    } else if (isFiltering) {
      fillColor = "#edf2f7";
      fillOpacity = 0.45;
      color = "#cbd5e1";
      weight = 0.8;
    }

    if (pid === selectedId) {
      color = "#f59e0b";
      weight = 3;
      fillOpacity = 0.94;
    }

    return { fillColor, fillOpacity, color, weight };
  }

  function applySelectedStyle(layer) {
    layer.setStyle({
      color: "#f59e0b",
      weight: 3,
      fillOpacity: 0.94,
    });
    layer.bringToFront();
  }

  function buildTooltipHtml(pid) {
    const info = summaryById[pid];
    if (!info) return "";

    const title = window.I18n.provinceName(pid, info.name);
    const mineralsHtml = info.minerals
      .map(
        (m) =>
          `<span class="tt-badge" style="border-left: 3px solid ${window.I18n.groupColor(m.mineral_group)}">${window.I18n.mineralName(m.id, m.name)}</span>`
      )
      .join("");

    let highlightHtml = "";
    if (info.highlights && info.highlights.length > 0) {
      const h = info.highlights[0];
      highlightHtml = `<div class="tt-highlight">${window.I18n.mineralName(h.mineral_id, h.mineral_name)}: ${window.I18n.formatNumber(h.value)} ${h.unit || ""} (${h.period})</div>`;
    }

    return `
      <div class="tt-title">${title}</div>
      <div class="tt-merged">${info.merged_from}</div>
      ${mineralsHtml ? `<div class="tt-minerals">${mineralsHtml}</div>` : ""}
      ${highlightHtml}
      <div class="tt-hint">${info.distinct_mineral_count} ${window.I18n.t("tooltip_minerals_count")} · ${window.I18n.t("tooltip_click_hint")}</div>
    `;
  }

  function updateTooltipContent(pid, layer) {
    const html = buildTooltipHtml(pid);
    if (!layer.getTooltip()) {
      layer.bindTooltip(html, {
        sticky: true,
        direction: "top",
        offset: [0, -8],
        className: "mineral-tooltip",
      });
    } else {
      layer.setTooltipContent(html);
    }
    layer.openTooltip();
  }

  function updateData(provincesSummary, filters) {
    summaryById = {};
    provincesSummary.forEach((p) => {
      summaryById[p.id] = p;
    });
    activeFilters = { ...filters };

    if (geojsonLayer) {
      geojsonLayer.setStyle((feature) => styleForFeature(feature));
      if (selectedId && layersById[selectedId]) {
        applySelectedStyle(layersById[selectedId]);
      }
    }
    renderLegend();
  }

  function selectProvince(pid, zoomToLayer = true) {
    selectedId = pid;
    if (geojsonLayer) {
      geojsonLayer.setStyle((feature) => styleForFeature(feature));
    }
    const layer = layersById[pid];
    if (layer) {
      applySelectedStyle(layer);
      if (zoomToLayer && map) {
        map.fitBounds(layer.getBounds(), {
          paddingTopLeft: [40, 40],
          paddingBottomRight: [440, 40],
          maxZoom: 8,
          animate: true,
        });
      }
    }
  }

  function clearSelection() {
    selectedId = null;
    if (geojsonLayer) {
      geojsonLayer.setStyle((feature) => styleForFeature(feature));
    }
  }

  function fitVietnam() {
    if (map && geojsonLayer) {
      map.fitBounds(geojsonLayer.getBounds(), { padding: [24, 24] });
    }
  }

  function toggleBasemap() {
    if (!map || !tileLayer) return false;
    tilesEnabled = !tilesEnabled;
    if (tilesEnabled) {
      tileLayer.addTo(map);
      tileLayer.bringToBack();
    } else {
      map.removeLayer(tileLayer);
    }
    return tilesEnabled;
  }

  function renderLegend() {
    const el = document.getElementById("map-legend");
    if (!el) return;
    const palette = getPalette();
    const isFiltering = Boolean(
      activeFilters.group || activeFilters.mineral_id || activeFilters.metric_type || activeFilters.q
    );

    el.innerHTML = `
      <div class="legend-title">${window.I18n.t("legend_title")}</div>
      <div class="legend-item">
        <span class="legend-swatch" style="background:${palette.high}"></span>
        <span>${window.I18n.t("legend_2")}</span>
      </div>
      <div class="legend-item">
        <span class="legend-swatch" style="background:${palette.low}"></span>
        <span>${window.I18n.t("legend_1")}</span>
      </div>
      <div class="legend-item">
        <span class="legend-swatch" style="background:${isFiltering ? "#edf2f7" : "#e2e8f0"}"></span>
        <span>${window.I18n.t(isFiltering ? "legend_unmatched" : "legend_none")}</span>
      </div>
    `;
  }

  function refreshLanguage() {
    addIslandMarkers();
    renderLegend();
  }

  return {
    init,
    updateData,
    selectProvince,
    clearSelection,
    fitVietnam,
    toggleBasemap,
    refreshLanguage,
  };
})();
