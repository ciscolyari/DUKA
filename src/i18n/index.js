// Lightweight runtime translator: swaps known English UI text for Kiswahili and back.
// Original English is remembered per DOM node, so switching languages is lossless.
import { sw, patterns } from './sw';
const KEY = 'duka_lang', ATTRS = ['placeholder', 'title', 'aria-label'];
let lang = 'en', obs = null;
const textOrig = new WeakMap(), attrOrig = new WeakMap();
export const getLang = () => lang;

function tr(str) {
  const core = str.trim(); if (!core) return str;
  const lead = str.slice(0, str.indexOf(core)), trail = str.slice(lead.length + core.length);
  let out = sw[core];
  if (out === undefined) for (const [re, fn] of patterns) { const m = core.match(re); if (m) { out = fn(m, tr); break; } }
  return out === undefined ? str : lead + out + trail;
}
function doText(n) {
  const cur = n.nodeValue, o = textOrig.get(n);
  if (lang === 'sw') {
    if (o !== undefined && tr(o) === cur) return;
    const t = tr(cur);
    if (t !== cur) { textOrig.set(n, cur); n.nodeValue = t; } else textOrig.delete(n);
  } else if (o !== undefined) { textOrig.delete(n); if (cur === tr(o)) n.nodeValue = o; }
}
function doAttrs(el) {
  let rec = attrOrig.get(el); if (!rec) { rec = {}; attrOrig.set(el, rec); }
  for (const a of ATTRS) {
    const cur = el.getAttribute(a); if (cur == null) continue; const o = rec[a];
    if (lang === 'sw') {
      if (o !== undefined && tr(o) === cur) continue;
      const t = tr(cur); if (t !== cur) { rec[a] = cur; el.setAttribute(a, t); } else delete rec[a];
    } else if (o !== undefined) { delete rec[a]; if (cur === tr(o)) el.setAttribute(a, o); }
  }
}
function walk(node) {
  if (node.nodeType === 3) return doText(node);
  if (node.nodeType !== 1 || /^(SCRIPT|STYLE)$/.test(node.tagName)) return;
  doAttrs(node); node.childNodes.forEach(walk);
}
function start() {
  if (obs) return;
  obs = new MutationObserver((ms) => ms.forEach((m) => m.type === 'characterData' ? doText(m.target) : m.type === 'attributes' ? doAttrs(m.target) : m.addedNodes.forEach(walk)));
  obs.observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS });
}
export function setLang(l) {
  lang = l; try { localStorage.setItem(KEY, l); } catch { /* ignore */ }
  document.documentElement.lang = l; start(); walk(document.body);
}
try { lang = localStorage.getItem(KEY) || 'en'; } catch { /* ignore */ }
document.documentElement.lang = lang; start(); walk(document.body);
