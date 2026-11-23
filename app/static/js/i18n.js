window.I18n = (() => {
  const dict = window.__INITIAL_I18N__ || {};
  const provinceEnNames = window.__PROVINCE_EN_NAMES__ || {};
  let lang = localStorage.getItem("vn_mineral_lang") || "vi";
  if (!dict[lang]) lang = "vi";

  function getLang() {
    return lang;
  }

  function setLang(nextLang) {
    if (!dict[nextLang]) return;
    lang = nextLang;
    localStorage.setItem("vn_mineral_lang", lang);
    document.documentElement.lang = lang;
    applyDomTranslations();
  }

  function t(key) {
    return (dict[lang] && dict[lang][key]) || (dict.vi && dict.vi[key]) || key;
  }

  function mineralGroup(group) {
    return (dict[lang]?.mineral_groups?.[group]) || group;
  }

  function metricType(mt) {
    return (dict[lang]?.metric_types?.[mt]) || mt;
  }

  function provinceType(pt) {
    return (dict[lang]?.province_types?.[pt]) || pt;
  }

  function mineralName(id, fallbackVi) {
    return (dict[lang]?.mineral_names?.[id]) || fallbackVi || id;
  }

  function provinceName(id, fallbackVi) {
    if (lang === "en" && provinceEnNames[id]) {
      return provinceEnNames[id];
    }
    return fallbackVi || id;
  }

  function groupChipClass(group) {
    if (group === "Năng lượng") return "chip-energy";
    if (group === "Kim loại") return "chip-metallic";
    return "chip-nonmetallic";
  }

  function groupColor(group) {
    if (group === "Năng lượng") return "#d97706";
    if (group === "Kim loại") return "#2563eb";
    return "#059669";
  }

  function formatNumber(val) {
    if (val === null || val === undefined) return "";
    const locale = lang === "vi" ? "vi-VN" : "en-US";
    return new Intl.NumberFormat(locale, { maximumFractionDigits: 2 }).format(val);
  }

  function applyDomTranslations() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      el.placeholder = t(el.dataset.i18nPlaceholder);
    });
    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === lang);
    });
  }

  return {
    getLang,
    setLang,
    t,
    mineralGroup,
    metricType,
    provinceType,
    mineralName,
    provinceName,
    groupChipClass,
    groupColor,
    formatNumber,
    applyDomTranslations,
  };
})();
