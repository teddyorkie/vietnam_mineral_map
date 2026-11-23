(() => {
  const state = {
    filtersMeta: null,
    provincesData: [],
    statsData: null,
    selectedProvinceId: null,
    selectedDetail: null,
    filters: {
      group: "",
      mineral_id: "",
      metric_type: "",
      q: "",
    },
  };

  let searchTimer = null;

  async function fetchJson(url) {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status} for ${url}`);
    }
    return resp.json();
  }

  function buildQueryParams(paramsObj) {
    const params = new URLSearchParams();
    Object.entries(paramsObj).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }

  async function bootstrap() {
    window.I18n.applyDomTranslations();
    wireEvents();

    const [geojson, filtersMeta] = await Promise.all([
      fetchJson("/api/geojson"),
      fetchJson("/api/filters"),
    ]);

    state.filtersMeta = filtersMeta;
    document.getElementById("kpi-provinces").textContent = String(filtersMeta.provinces.length);
    document.getElementById("kpi-minerals").textContent = String(filtersMeta.minerals.length);

    renderFilterControls();
    window.MineralMap.init("map", geojson, (pid) => openProvinceDetail(pid));
    await refreshFilteredData();
  }

  function wireEvents() {
    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        window.I18n.setLang(btn.dataset.lang);
        renderFilterControls();
        renderProvinceList();
        window.MineralMap.refreshLanguage();
        if (state.selectedDetail) {
          renderProvinceDetail(state.selectedDetail);
        }
        if (document.getElementById("stats-modal").classList.contains("open")) {
          window.MineralCharts.renderAll(state.statsData, handleChartProvinceClick);
        }
      });
    });

    document.getElementById("search-input").addEventListener("input", (e) => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.filters.q = e.target.value.trim();
        refreshFilteredData();
      }, 180);
    });

    document.getElementById("mineral-select").addEventListener("change", (e) => {
      state.filters.mineral_id = e.target.value;
      refreshFilteredData();
    });

    document.getElementById("metric-select").addEventListener("change", (e) => {
      state.filters.metric_type = e.target.value;
      refreshFilteredData();
    });

    document.getElementById("btn-reset-filters").addEventListener("click", () => {
      state.filters = { group: "", mineral_id: "", metric_type: "", q: "" };
      document.getElementById("search-input").value = "";
      renderFilterControls();
      refreshFilteredData();
    });

    document.getElementById("btn-reset-view").addEventListener("click", () => {
      window.MineralMap.fitVietnam();
    });

    document.getElementById("btn-toggle-basemap").addEventListener("click", (e) => {
      const enabled = window.MineralMap.toggleBasemap();
      e.currentTarget.classList.toggle("active", enabled);
      e.currentTarget.textContent = window.I18n.t(
        enabled ? "btn_basemap_clean" : "btn_basemap_tiles"
      );
    });

    document.getElementById("btn-close-drawer").addEventListener("click", closeDrawer);

    document.getElementById("btn-open-stats").addEventListener("click", openStatsModal);
    document.getElementById("btn-close-stats").addEventListener("click", closeStatsModal);
    document.getElementById("stats-modal").addEventListener("click", (e) => {
      if (e.target.id === "stats-modal") closeStatsModal();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeStatsModal();
        closeDrawer();
      }
    });
  }

  function renderFilterControls() {
    if (!state.filtersMeta) return;

    // Group pills
    const pillsWrap = document.getElementById("group-pills");
    const allBtn = `<button type="button" class="group-pill ${!state.filters.group ? "active" : ""}" data-group="">${window.I18n.t("all_groups")}</button>`;
    const groupBtns = state.filtersMeta.mineral_groups
      .map((g) => {
        const active = state.filters.group === g ? "active" : "";
        return `<button type="button" class="group-pill ${active}" data-group="${g}"><span class="dot" style="background:${window.I18n.groupColor(g)}"></span>${window.I18n.mineralGroup(g)}</button>`;
      })
      .join("");
    pillsWrap.innerHTML = allBtn + groupBtns;

    pillsWrap.querySelectorAll(".group-pill").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.filters.group = btn.dataset.group;
        if (state.filters.group && state.filters.mineral_id) {
          const matchedMineral = state.filtersMeta.minerals.find(
            (m) => m.id === state.filters.mineral_id
          );
          if (matchedMineral && matchedMineral.mineral_group !== state.filters.group) {
            state.filters.mineral_id = "";
          }
        }
        renderFilterControls();
        refreshFilteredData();
      });
    });

    // Mineral dropdown (filtered by active group if chosen)
    const mineralSelect = document.getElementById("mineral-select");
    const visibleMinerals = state.filters.group
      ? state.filtersMeta.minerals.filter((m) => m.mineral_group === state.filters.group)
      : state.filtersMeta.minerals;

    mineralSelect.innerHTML =
      `<option value="">${window.I18n.t("all_minerals")}</option>` +
      visibleMinerals
        .map(
          (m) =>
            `<option value="${m.id}" ${state.filters.mineral_id === m.id ? "selected" : ""}>${window.I18n.mineralName(m.id, m.name)}</option>`
        )
        .join("");

    // Metric type dropdown
    const metricSelect = document.getElementById("metric-select");
    metricSelect.innerHTML =
      `<option value="">${window.I18n.t("all_metrics")}</option>` +
      state.filtersMeta.metric_types
        .map(
          (mt) =>
            `<option value="${mt}" ${state.filters.metric_type === mt ? "selected" : ""}>${window.I18n.metricType(mt)}</option>`
        )
        .join("");
  }

  async function refreshFilteredData() {
    const provQuery = buildQueryParams(state.filters);
    const statsQuery = buildQueryParams({
      group: state.filters.group,
      mineral_id: state.filters.mineral_id,
    });

    const [provRes, statsRes] = await Promise.all([
      fetchJson(`/api/provinces${provQuery}`),
      fetchJson(`/api/statistics${statsQuery}`),
    ]);

    state.provincesData = provRes.provinces;
    state.statsData = statsRes;

    document.getElementById("kpi-matched").textContent = String(provRes.matched_provinces);

    window.MineralMap.updateData(state.provincesData, state.filters);
    renderProvinceList();

    if (document.getElementById("stats-modal").classList.contains("open")) {
      window.MineralCharts.renderAll(state.statsData, handleChartProvinceClick);
    }
  }

  function renderProvinceList() {
    const listEl = document.getElementById("province-list");
    const isFiltering = Boolean(
      state.filters.group || state.filters.mineral_id || state.filters.metric_type || state.filters.q
    );

    const visible = isFiltering
      ? state.provincesData.filter((p) => p.has_match)
      : state.provincesData;

    if (visible.length === 0) {
      listEl.innerHTML = `<div class="empty-list">${window.I18n.t("no_results")}</div>`;
      return;
    }

    listEl.innerHTML = visible
      .map((p) => {
        const isSelected = p.id === state.selectedProvinceId;
        const chips = p.minerals
          .map(
            (m) =>
              `<span class="mineral-chip ${window.I18n.groupChipClass(m.mineral_group)}">${window.I18n.mineralName(m.id, m.name)}</span>`
          )
          .join("");

        return `
          <div class="province-item ${isSelected ? "selected" : ""} ${!p.has_match ? "dimmed" : ""}" data-province-id="${p.id}">
            <div class="province-item-top">
              <span class="province-item-name">${window.I18n.provinceName(p.id, p.name)}</span>
              <span class="province-item-count ${p.distinct_mineral_count > 0 ? "has-data" : ""}">
                ${p.distinct_mineral_count} ${window.I18n.t("tooltip_minerals_count")}
              </span>
            </div>
            <div class="province-item-merged">${p.merged_from}</div>
            ${chips ? `<div class="mineral-chip-row">${chips}</div>` : ""}
          </div>
        `;
      })
      .join("");

    listEl.querySelectorAll(".province-item").forEach((el) => {
      el.addEventListener("click", () => {
        const pid = el.dataset.provinceId;
        window.MineralMap.selectProvince(pid, true);
        openProvinceDetail(pid);
      });
    });
  }

  async function openProvinceDetail(provinceId) {
    state.selectedProvinceId = provinceId;
    renderProvinceList();

    const detail = await fetchJson(`/api/provinces/${encodeURIComponent(provinceId)}`);
    state.selectedDetail = detail;
    renderProvinceDetail(detail);

    const drawer = document.getElementById("detail-drawer");
    drawer.classList.add("open");
    drawer.setAttribute("aria-hidden", "false");
  }

  function renderProvinceDetail(detail) {
    document.getElementById("drawer-code").textContent = `#${detail.id}`;
    document.getElementById("drawer-title").textContent = window.I18n.provinceName(
      detail.id,
      detail.name
    );

    document.getElementById("drawer-badges").innerHTML = `
      <span class="meta-badge">${window.I18n.provinceType(detail.province_type)}</span>
      <span class="meta-badge">${detail.distinct_mineral_count} ${window.I18n.t("tooltip_minerals_count")}</span>
      <span class="meta-badge">${detail.record_count} ${window.I18n.t("tooltip_records_count")}</span>
    `;

    document.getElementById("drawer-meta").innerHTML = `
      <div><strong>${window.I18n.t("drawer_merged_from")}:</strong> ${detail.merged_from}</div>
      <div><strong>${window.I18n.t("drawer_coordinates")}:</strong> ${detail.lat.toFixed(4)}°N, ${detail.lng.toFixed(4)}°E</div>
    `;

    const bodyEl = document.getElementById("drawer-body");
    if (!detail.records || detail.records.length === 0) {
      bodyEl.innerHTML = `
        <div class="empty-drawer">
          <h3>${window.I18n.t("drawer_empty_title")}</h3>
          <p>${window.I18n.t("drawer_empty_desc")}</p>
        </div>
      `;
      return;
    }

    bodyEl.innerHTML = detail.records
      .map((rec) => {
        const chipClass = window.I18n.groupChipClass(rec.mineral_group);
        const valueHtml =
          rec.value !== null
            ? `<div><span class="record-value">${window.I18n.formatNumber(rec.value)}</span> <span class="record-unit">${rec.unit || ""}</span></div>`
            : `<div class="record-unit">${window.I18n.t("label_no_value")}</div>`;

        const reserveHtml =
          rec.national_reserve !== null
            ? `<div><strong>${window.I18n.t("label_national_reserve")}:</strong> ${window.I18n.formatNumber(rec.national_reserve)} ${rec.reserve_unit || ""}</div>`
            : "";

        const natProdHtml =
          rec.national_production && rec.national_production.length > 0
            ? `<div><strong>${window.I18n.t("label_national_prod")}:</strong> ${rec.national_production
                .map((p) => `${p.year}: ${window.I18n.formatNumber(p.value)} ${p.unit}`)
                .join(" → ")}</div>`
            : "";

        return `
          <article class="record-card">
            <div class="record-card-head">
              <span class="record-mineral-name">${window.I18n.mineralName(rec.mineral_id, rec.mineral_name)}</span>
              <span class="mineral-chip ${chipClass}">${window.I18n.mineralGroup(rec.mineral_group)}</span>
            </div>

            <div class="record-metric-box">
              ${valueHtml}
              <span class="metric-tag">${window.I18n.metricType(rec.metric_type)} · ${rec.period}</span>
            </div>

            <div class="record-field"><strong>${window.I18n.t("label_key_mines")}:</strong> ${rec.key_mines}</div>
            ${rec.notes ? `<div class="record-field"><strong>${window.I18n.t("label_notes")}:</strong> ${rec.notes}</div>` : ""}

            ${
              reserveHtml || natProdHtml
                ? `<div class="record-context">${reserveHtml}${natProdHtml}</div>`
                : ""
            }

            <a class="record-source" href="${rec.source_url}" target="_blank" rel="noopener noreferrer">
              ${window.I18n.t("label_source")} ↗
            </a>
          </article>
        `;
      })
      .join("");
  }

  function closeDrawer() {
    const drawer = document.getElementById("detail-drawer");
    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    state.selectedProvinceId = null;
    state.selectedDetail = null;
    window.MineralMap.clearSelection();
    renderProvinceList();
  }

  function openStatsModal() {
    const modal = document.getElementById("stats-modal");
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    window.MineralCharts.renderAll(state.statsData, handleChartProvinceClick);
  }

  function closeStatsModal() {
    const modal = document.getElementById("stats-modal");
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
  }

  function handleChartProvinceClick(provinceId) {
    closeStatsModal();
    window.MineralMap.selectProvince(provinceId, true);
    openProvinceDetail(provinceId);
  }

  document.addEventListener("DOMContentLoaded", () => {
    bootstrap().catch((err) => {
      console.error("Failed to initialize Vietnam Mineral Map:", err);
    });
  });
})();
