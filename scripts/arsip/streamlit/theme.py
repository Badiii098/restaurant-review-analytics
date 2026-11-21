"""LAPISAN 5 — Token desain dan gaya global antarmuka.

Acuan visual diambil dari draf desain yang dihasilkan Google Stitch
("Prioritas Perbaikan Layanan", desktop 1440 px dan mobile 390 px).
Arahnya tetap satu: **lembar laporan operasional**, bukan dasbor SaaS —
kertas tenang, garis rambut, angka rata kanan bertabular, satu warna
sorot.

Aturan yang dipegang berkas ini:

* satu warna sorot (hijau laut dalam ``#12564A``), tanpa gradien dan
  tanpa bayangan;
* radius sudut 2 px di semua elemen;
* struktur dibentuk garis rambut dan jarak, bukan tumpukan kartu;
* angka memakai ``tabular-nums`` supaya kolom tidak bergoyang;
* tanpa emoji dan tanpa animasi masuk.

Seluruh nilai warna dikumpulkan di ``PALETTE`` supaya komponen dan gaya
tidak pernah menyebut nilai warna secara langsung.
"""

from __future__ import annotations

from string import Template

PALETTE = {
    "canvas": "#F4F5F3",
    "surface": "#FFFFFF",
    "inset": "#FCFDFB",
    "hover": "#F9FAF9",
    "ink": "#14181A",
    "secondary": "#636C6A",
    "rule": "#DCE1DD",
    "rule_soft": "#EAEFEA",
    "accent": "#12564A",
    "accent_deep": "#0E443A",
    "accent_tint": "#E8EFEB",
    "amber": "#8A5A15",
    "amber_bg": "#FCF9F2",
    "amber_rule": "#E8DFC9",
    "amber_ink": "#5C4518",
    "amber_chip": "#F2E8D3",
}

FONT_STACK = (
    "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, "
    "'Noto Sans', 'Ubuntu', sans-serif"
)
FONT_IMPORT = (
    "https://fonts.googleapis.com/css2"
    "?family=Inter:wght@400;500;600;700&display=swap"
)

CSS = Template("""
<style>
@import url("$font_import");

:root {
  --rra-canvas: $canvas;
  --rra-surface: $surface;
  --rra-inset: $inset;
  --rra-hover: $hover;
  --rra-ink: $ink;
  --rra-secondary: $secondary;
  --rra-rule: $rule;
  --rra-rule-soft: $rule_soft;
  --rra-accent: $accent;
  --rra-accent-deep: $accent_deep;
  --rra-accent-tint: $accent_tint;
  --rra-amber: $amber;
  --rra-amber-bg: $amber_bg;
  --rra-amber-rule: $amber_rule;
  --rra-amber-ink: $amber_ink;
  --rra-amber-chip: $amber_chip;
  --rra-font: $font;
  --rra-topbar: 44px;
}

/* ------------------------------------------------------------------ */
/* Kerangka halaman                                                     */
/* ------------------------------------------------------------------ */
html, body, [class*="css"], .stApp {
  font-family: var(--rra-font);
  background: var(--rra-canvas);
  color: var(--rra-ink);
  font-size: 13.5px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebarNav"],
#MainMenu, footer { display: none !important; }

.block-container {
  max-width: 1160px;
  padding: calc(var(--rra-topbar) + 2.5rem) 2.5rem 3rem;
}
[data-testid="stSidebar"] {
  background: var(--rra-surface);
  border-right: 1px solid var(--rra-rule);
  width: 280px !important;
  min-width: 280px !important;
  max-width: 280px !important;
}
[data-testid="stSidebarContent"] {
  padding: calc(var(--rra-topbar) + 1.5rem) 1.5rem 2rem;
}
[data-testid="stSidebar"] .block-container { max-width: 100%; padding: 0; }

/* ------------------------------------------------------------------ */
/* Bilah atas (kepala berkas institusional)                             */
/* ------------------------------------------------------------------ */
.rra-topbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--rra-topbar);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--rra-surface);
  border-bottom: 1px solid var(--rra-rule);
  padding: 0 2rem;
  font-size: 12px;
  color: var(--rra-secondary);
  z-index: 1000;
}
.rra-topbar-left, .rra-topbar-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.rra-brand { color: var(--rra-ink); font-weight: 600; letter-spacing: -0.01em; }
.rra-sep { display: inline-block; width: 1px; height: 12px; background: var(--rra-rule); }
.rra-chip {
  display: inline-block;
  background: var(--rra-accent-tint);
  color: var(--rra-accent);
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 2px;
}
code, .rra-code {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  font-size: 11.5px;
  background: var(--rra-canvas);
  border: 1px solid var(--rra-rule);
  border-radius: 2px;
  padding: 1px 4px;
  color: var(--rra-ink);
}

/* ------------------------------------------------------------------ */
/* Kartu bagian                                                         */
/* ------------------------------------------------------------------ */
.rra-card {
  background: var(--rra-surface);
  border: 1px solid var(--rra-rule);
  border-radius: 2px;
  padding: 1.75rem;
  margin: 0 0 2rem;
}
.rra-card > *:last-child { margin-bottom: 0; }
.rra-sec-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid var(--rra-rule);
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}
.rra-sec-head h2 {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.005em;
  margin: 0;
}
.rra-sec-note {
  font-size: 12px;
  color: var(--rra-secondary);
  text-align: right;
  margin: 0;
}
.rra-sec-sub {
  font-size: 12px;
  color: var(--rra-secondary);
  margin: -0.75rem 0 1rem;
}
.rra-card-note {
  border-top: 1px solid var(--rra-rule);
  margin-top: 1rem;
  padding-top: 0.75rem;
  font-size: 12px;
  line-height: 1.6;
  color: var(--rra-secondary);
}

/* ------------------------------------------------------------------ */
/* Kepala laporan                                                       */
/* ------------------------------------------------------------------ */
.rra-head h1 {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.18;
  margin: 0 0 0.5rem;
}
.rra-lead {
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  max-width: 78ch;
}
.rra-lead strong { font-weight: 700; }
.rra-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 1.25rem 0 0;
  padding-top: 1rem;
  border-top: 1px solid var(--rra-rule);
}
.rra-meta > div {
  padding-right: 1.25rem;
  border-right: 1px solid var(--rra-rule);
}
.rra-meta > div + div { padding-left: 1.25rem; }
.rra-meta > div:last-child { border-right: 0; padding-right: 0; }
.rra-meta dt {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--rra-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 0.25rem;
}
.rra-meta dd {
  font-size: 13px;
  font-weight: 500;
  margin: 0;
  font-variant-numeric: tabular-nums;
}

/* ------------------------------------------------------------------ */
/* Angka ringkas                                                        */
/* ------------------------------------------------------------------ */
.rra-figures {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.rra-figures > div {
  padding-right: 1.5rem;
  border-right: 1px solid var(--rra-rule);
}
.rra-figures > div + div { padding-left: 1.5rem; }
.rra-figures > div:last-child { border-right: 0; padding-right: 0; }
.rra-fig-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.05;
  font-variant-numeric: tabular-nums;
}
.rra-fig-label {
  display: block;
  font-size: 12.5px;
  color: var(--rra-secondary);
  margin-top: 0.35rem;
}

/* ------------------------------------------------------------------ */
/* Peringatan                                                           */
/* ------------------------------------------------------------------ */
.rra-alert {
  background: var(--rra-amber-bg);
  border: 1px solid var(--rra-amber-rule);
  border-left: 4px solid var(--rra-amber);
  border-radius: 2px;
  padding: 0.9rem 1rem;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin: 0 0 1.5rem;
}
.rra-alert-title {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--rra-amber);
  margin: 0 0 0.15rem;
}
.rra-alert-text {
  font-size: 12px;
  line-height: 1.6;
  color: var(--rra-amber-ink);
  margin: 0;
}
.rra-alert-chip {
  flex: 0 0 auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 11px;
  font-weight: 500;
  color: var(--rra-amber);
  background: var(--rra-amber-chip);
  border-radius: 2px;
  padding: 2px 8px;
}

/* ------------------------------------------------------------------ */
/* Tabel                                                                */
/* ------------------------------------------------------------------ */
.rra-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
}
.rra-table th {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--rra-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.6rem 0.5rem 0.55rem 0;
  border-bottom: 1px solid var(--rra-rule);
  white-space: nowrap;
}
.rra-table td {
  padding: 0.75rem 0.5rem 0.75rem 0;
  border-bottom: 1px solid var(--rra-rule);
  vertical-align: top;
}
.rra-table tbody tr:last-child td { border-bottom: 0; }
.rra-table .n { text-align: right; font-variant-numeric: tabular-nums; }
.rra-table th.n { text-align: right; }

.rra-rank .rra-idx {
  width: 3rem;
  text-align: center;
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  color: var(--rra-secondary);
}
.rra-rank th.rra-idx { text-align: center; }
.rra-rank tr.is-first td {
  background: var(--rra-accent-tint);
  border-bottom-color: var(--rra-rule);
}
.rra-rank tr.is-first td:first-child { box-shadow: inset 2px 0 0 var(--rra-accent); }
.rra-rank tr.is-first .rra-idx { color: var(--rra-accent); font-weight: 700; }
.rra-rank tbody tr:not(.is-first):hover td { background: var(--rra-hover); }
.rra-aspect { display: block; font-weight: 600; }
.rra-rank tr.is-first .rra-aspect { font-weight: 700; }
.rra-sub {
  display: block;
  font-size: 11.5px;
  color: var(--rra-secondary);
  margin-top: 0.15rem;
  font-variant-numeric: tabular-nums;
}
.rra-rank .rra-score { font-size: 13.5px; font-weight: 500; }
.rra-rank tr.is-first .rra-score { font-size: 14px; font-weight: 700; color: var(--rra-accent); }
.rra-w-aspect { width: 22rem; }
.rra-w-count { width: 9rem; }
.rra-w-score { width: 9rem; }
.rra-w-value { width: 6rem; }

.rra-actions td:first-child { width: 10rem; font-weight: 600; }
.rra-actions td:nth-child(2) {
  width: 12rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}
.rra-actions td:last-child { line-height: 1.6; }
.rra-actions tr.is-first td:first-child { font-weight: 700; color: var(--rra-accent); }

/* ------------------------------------------------------------------ */
/* Batang                                                               */
/* ------------------------------------------------------------------ */
.rra-bar {
  display: block;
  position: relative;
  height: 6px;
  border-radius: 1px;
  background: var(--rra-rule-soft);
  overflow: hidden;
}
.rra-bar > i {
  position: absolute;
  inset: 0 auto 0 0;
  display: block;
  background: var(--rra-secondary);
}
.rra-rank tr.is-first .rra-bar { background: var(--rra-rule); }
.rra-rank tr.is-first .rra-bar > i { background: var(--rra-accent); }

/* ------------------------------------------------------------------ */
/* Frasa keluhan                                                        */
/* ------------------------------------------------------------------ */
.rra-phrases {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
}
.rra-ph {
  border: 1px solid var(--rra-rule);
  border-radius: 2px;
  padding: 1rem;
  background: var(--rra-surface);
}
.rra-ph.wide { grid-column: span 2; }
.rra-ph-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  border-bottom: 1px solid var(--rra-rule);
  padding-bottom: 0.5rem;
  margin-bottom: 0.75rem;
}
.rra-ph-head h3 { font-size: 13.5px; font-weight: 700; margin: 0; }
.rra-ph-head span {
  font-size: 12px;
  color: var(--rra-secondary);
  font-variant-numeric: tabular-nums;
}
.rra-ph-head span.is-first { color: var(--rra-accent); font-weight: 600; }
.rra-ph-items { display: grid; gap: 0.6rem; }
.rra-ph.wide .rra-ph-items { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.5rem; }
.rra-ph-line {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 12px;
  margin-bottom: 0.25rem;
}
.rra-ph-line .t { font-weight: 500; }
.rra-ph-line .n { color: var(--rra-secondary); font-variant-numeric: tabular-nums; }
.rra-ph-track {
  display: block;
  position: relative;
  height: 4px;
  border-radius: 1px;
  background: var(--rra-canvas);
  overflow: hidden;
}
.rra-ph-track > i {
  position: absolute;
  inset: 0 auto 0 0;
  display: block;
  background: var(--rra-secondary);
}
.rra-ph.is-first .rra-ph-track > i { background: var(--rra-accent); }
.rra-ph-empty { font-size: 12px; color: var(--rra-secondary); margin: 0; }

/* ------------------------------------------------------------------ */
/* Bahan audit                                                          */
/* ------------------------------------------------------------------ */
.rra-audit {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2rem;
}
.rra-formula {
  border: 1px solid var(--rra-rule);
  border-radius: 2px;
  background: var(--rra-inset);
  padding: 1rem;
}
.rra-label {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--rra-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 0.5rem;
}
.rra-formula code, .rra-eq {
  display: block;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
  color: var(--rra-accent);
  background: var(--rra-surface);
  border: 1px solid var(--rra-rule);
  border-radius: 2px;
  padding: 0.75rem;
  margin: 0 0 0.75rem;
  user-select: all;
}
.rra-weights {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  font-size: 12px;
}
.rra-weights > div { border-left: 2px solid var(--rra-accent); padding-left: 0.5rem; }
.rra-weights span {
  display: block;
  color: var(--rra-secondary);
  font-size: 11.5px;
}
.rra-weights b {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.rra-block-title { font-size: 12px; font-weight: 600; margin: 1.25rem 0 0.5rem; }
.rra-timings { width: 100%; border-collapse: collapse; font-size: 12px; }
.rra-timings td {
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--rra-rule);
  color: var(--rra-secondary);
}
.rra-timings td:last-child {
  text-align: right;
  color: var(--rra-ink);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.rra-timings tr.total td {
  background: var(--rra-canvas);
  font-weight: 600;
  color: var(--rra-ink);
  padding-left: 0.25rem;
  padding-right: 0.25rem;
}
.rra-trace {
  border: 1px solid var(--rra-rule);
  border-radius: 2px;
  padding: 1.25rem;
  background: var(--rra-surface);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.rra-trace h3 { font-size: 13px; font-weight: 700; margin: 0 0 0.75rem; }
.rra-trace ul { list-style: none; margin: 0; padding: 0; }
.rra-trace li {
  display: flex;
  gap: 0.5rem;
  font-size: 12.5px;
  line-height: 1.6;
  padding: 0.3rem 0;
}
.rra-trace li .dot { color: var(--rra-accent); font-weight: 700; line-height: 1.5; }
.rra-trace-foot {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  border-top: 1px solid var(--rra-rule);
  margin-top: 1.5rem;
  padding-top: 0.75rem;
  font-size: 11px;
  color: var(--rra-secondary);
}

/* ------------------------------------------------------------------ */
/* Bilah samping                                                        */
/* ------------------------------------------------------------------ */
.rra-side-title {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 0.25rem;
}
.rra-side-caption {
  font-size: 12px;
  line-height: 1.6;
  color: var(--rra-secondary);
  margin: 0 0 1rem;
}
.rra-side-block {
  border-top: 1px solid var(--rra-rule);
  margin-top: 1.5rem;
  padding-top: 1.25rem;
}
.rra-side-block .rra-label { margin-bottom: 0.75rem; }
.rra-kv { width: 100%; border-collapse: collapse; font-size: 12px; }
.rra-kv td { padding: 0.3rem 0; vertical-align: baseline; }
.rra-kv td:first-child { color: var(--rra-secondary); }
.rra-kv td:last-child {
  text-align: right;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
.rra-kv tr.mono td:last-child {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 11.5px;
}
.rra-kv tr.accent td:last-child { color: var(--rra-accent); font-weight: 600; }
.rra-side-inset {
  background: var(--rra-canvas);
  border: 1px solid var(--rra-rule);
  border-radius: 2px;
  padding: 0.75rem;
  font-size: 11.5px;
  line-height: 1.6;
  color: var(--rra-secondary);
}
.rra-side-inset b { display: block; color: var(--rra-ink); font-weight: 600; margin-bottom: 0.25rem; }
.rra-side-inset q {
  display: block;
  border-left: 2px solid var(--rra-rule);
  padding-left: 0.5rem;
  margin-top: 0.5rem;
  font-style: italic;
}
.rra-side-foot {
  border-top: 1px solid var(--rra-rule);
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  font-size: 11px;
  color: var(--rra-secondary);
}
.rra-side-foot b { display: block; color: var(--rra-ink); font-weight: 500; }

/* ------------------------------------------------------------------ */
/* Kaki halaman                                                         */
/* ------------------------------------------------------------------ */
.rra-page-foot {
  border-top: 1px solid var(--rra-rule);
  margin-top: 0.5rem;
  padding: 1rem 0 2rem;
  text-align: center;
  font-size: 12px;
  color: var(--rra-secondary);
}

/* ------------------------------------------------------------------ */
/* Kendali Streamlit                                                    */
/* ------------------------------------------------------------------ */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  font-size: 12px !important;
  font-weight: 600 !important;
  color: var(--rra-ink) !important;
  margin-bottom: 0.35rem !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
  font-size: 11.5px !important;
  color: var(--rra-secondary) !important;
  line-height: 1.55 !important;
}
[data-baseweb="select"] > div {
  border-radius: 2px !important;
  border-color: var(--rra-rule) !important;
  min-height: 36px !important;
  font-size: 13px !important;
  background: var(--rra-surface) !important;
}
[data-baseweb="select"] svg { color: var(--rra-secondary); }
[data-testid="stTextInput"] input {
  border-radius: 2px !important;
  border-color: var(--rra-rule) !important;
  font-size: 12.5px !important;
  min-height: 36px !important;
}
[data-testid="stTextInput"] input:disabled {
  background: var(--rra-canvas) !important;
  color: var(--rra-ink) !important;
  -webkit-text-fill-color: var(--rra-ink) !important;
}
.stButton > button {
  width: 100%;
  border-radius: 2px;
  border: 0;
  background: var(--rra-accent);
  color: #FFFFFF;
  font-size: 12.5px;
  font-weight: 600;
  min-height: 36px;
  padding: 0.4rem 0.9rem;
  transition: background 120ms ease;
}
.stButton > button:hover,
.stButton > button:focus {
  background: var(--rra-accent-deep);
  color: #FFFFFF;
}
.stButton > button:focus-visible {
  outline: 2px solid var(--rra-accent);
  outline-offset: 2px;
}
[data-testid="stAlert"] {
  border-radius: 2px;
  border: 1px solid var(--rra-rule);
  font-size: 12.5px;
}
[data-testid="stSpinner"] p { font-size: 12.5px; color: var(--rra-secondary); }
[data-testid="stMarkdownContainer"] p { margin-bottom: 0; }
::selection { background: var(--rra-accent-tint); }

/* ------------------------------------------------------------------ */
/* Tanggap ukuran                                                       */
/* ------------------------------------------------------------------ */
@media (max-width: 1100px) {
  .block-container { padding: calc(var(--rra-topbar) + 1.5rem) 1.25rem 3rem; }
  .rra-card { padding: 1.25rem; }
  .rra-meta, .rra-figures { grid-template-columns: repeat(2, minmax(0, 1fr)); row-gap: 1rem; }
  .rra-meta > div:nth-child(2), .rra-figures > div:nth-child(2) { border-right: 0; }
  .rra-phrases, .rra-audit { grid-template-columns: minmax(0, 1fr); }
  .rra-ph.wide { grid-column: span 1; }
  .rra-ph.wide .rra-ph-items { grid-template-columns: minmax(0, 1fr); }
  .rra-head h1 { font-size: 22px; }
  .rra-topbar { padding: 0 1.25rem; }
  .rra-topbar-left { gap: 0.75rem; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
</style>
""").safe_substitute(font=FONT_STACK, font_import=FONT_IMPORT, **PALETTE)
