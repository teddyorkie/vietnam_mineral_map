window.MineralCharts = (() => {
  const instances = {};

  function destroyIfExists(key) {
    if (instances[key]) {
      instances[key].destroy();
      delete instances[key];
    }
  }

  function renderAll(stats, onSelectProvince) {
    if (!stats || typeof Chart === "undefined") return;
    renderRanking(stats.province_ranking || [], onSelectProvince);
    renderGroups(stats.group_breakdown || []);
    renderReserves(stats.national_reserves || []);
    renderProduction(stats.national_production || { years: [], items: [] });
  }

  function renderRanking(ranking, onSelectProvince) {
    destroyIfExists("ranking");
    const ctx = document.getElementById("chart-ranking");
    if (!ctx) return;

    const top = ranking.slice(0, 10);
    instances.ranking = new Chart(ctx, {
      type: "bar",
      data: {
        labels: top.map((r) => window.I18n.provinceName(r.province_id, r.province_name)),
        datasets: [
          {
            label: window.I18n.t("chart_label_distinct"),
            data: top.map((r) => r.distinct_minerals),
            backgroundColor: "#0284c7",
            borderRadius: 5,
          },
          {
            label: window.I18n.t("chart_label_records"),
            data: top.map((r) => r.record_count),
            backgroundColor: "#94a3b8",
            borderRadius: 5,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        onClick: (_evt, elements) => {
          if (elements.length > 0 && onSelectProvince) {
            const idx = elements[0].index;
            onSelectProvince(top[idx].province_id);
          }
        },
        scales: {
          x: { beginAtZero: true, ticks: { stepSize: 1 } },
        },
        plugins: {
          legend: { position: "bottom" },
        },
      },
    });
  }

  function renderGroups(groups) {
    destroyIfExists("groups");
    const ctx = document.getElementById("chart-groups");
    if (!ctx) return;

    instances.groups = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: groups.map((g) => window.I18n.mineralGroup(g.group)),
        datasets: [
          {
            data: groups.map((g) => g.record_count),
            backgroundColor: groups.map((g) => window.I18n.groupColor(g.group)),
            borderWidth: 2,
            borderColor: "#ffffff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
        },
      },
    });
  }

  function renderReserves(reserves) {
    destroyIfExists("reserves");
    const ctx = document.getElementById("chart-reserves");
    if (!ctx) return;

    instances.reserves = new Chart(ctx, {
      type: "bar",
      data: {
        labels: reserves.map((r) => window.I18n.mineralName(r.mineral_id, r.mineral_name)),
        datasets: [
          {
            label: window.I18n.t("label_national_reserve"),
            data: reserves.map((r) => r.national_reserve),
            backgroundColor: reserves.map((r) => window.I18n.groupColor(r.mineral_group)),
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => {
                const item = reserves[context.dataIndex];
                return `${window.I18n.formatNumber(item.national_reserve)} ${item.reserve_unit || ""}`;
              },
            },
          },
        },
      },
    });
  }

  function renderProduction(prod) {
    destroyIfExists("production");
    const ctx = document.getElementById("chart-production");
    if (!ctx) return;

    const years = prod.years || [];
    const items = prod.items || [];
    const yearColors = ["#64748b", "#0ea5e9", "#059669", "#d97706"];

    instances.production = new Chart(ctx, {
      type: "bar",
      data: {
        labels: items.map((it) => window.I18n.mineralName(it.mineral_id, it.mineral_name)),
        datasets: years.map((yr, idx) => ({
          label: String(yr),
          data: items.map((it) => it.series[String(yr)] ?? null),
          backgroundColor: yearColors[idx % yearColors.length],
          borderRadius: 5,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true },
        },
        plugins: {
          legend: { position: "bottom" },
          tooltip: {
            callbacks: {
              label: (context) => {
                const item = items[context.dataIndex];
                return `${context.dataset.label}: ${window.I18n.formatNumber(context.parsed.y)} ${item.unit}`;
              },
            },
          },
        },
      },
    });
  }

  return { renderAll };
})();
