/**
 * i18n.js
 * -------
 * Minimal, dependency-free language switcher.
 *
 * How it works:
 *  - Translation strings live in /static/i18n/<lang>.json (en, hi, ta, te)
 *  - Any element with data-i18n="key" gets its textContent replaced
 *  - Any element with data-i18n-placeholder="key" gets its placeholder replaced
 *  - Selected language is remembered (in-memory + URL-independent via a cookie)
 *
 * To add real translations: edit static/i18n/hi.json, ta.json, te.json
 * and replace the English fallback values with translated text. No other
 * code needs to change.
 */

const SUPPORTED_LANGS = ["en", "hi", "ta", "te"];
const DEFAULT_LANG = "en";

function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name, value) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=31536000`;
}

async function loadTranslations(lang) {
  try {
    const res = await fetch(`/static/i18n/${lang}.json`);
    if (!res.ok) throw new Error("missing translation file");
    return await res.json();
  } catch (err) {
    console.warn(`i18n: could not load ${lang}, falling back to ${DEFAULT_LANG}`, err);
    if (lang !== DEFAULT_LANG) return loadTranslations(DEFAULT_LANG);
    return {};
  }
}

function applyTranslations(dict) {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key]) el.setAttribute("placeholder", dict[key]);
  });
}

async function setLanguage(lang) {
  if (!SUPPORTED_LANGS.includes(lang)) lang = DEFAULT_LANG;
  const dict = await loadTranslations(lang);
  applyTranslations(dict);
  document.documentElement.setAttribute("lang", lang);
  setCookie("disasteraid_lang", lang);
  const select = document.getElementById("langSelect");
  if (select) select.value = lang;
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = getCookie("disasteraid_lang") || DEFAULT_LANG;
  setLanguage(saved);

  const select = document.getElementById("langSelect");
  if (select) {
    select.addEventListener("change", (e) => setLanguage(e.target.value));
  }
});
