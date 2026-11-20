import { useState } from "react";

export interface Seri { nama: string; warna: "series-1" | "series-2" }
export interface Baris { label: string; nilai: (number | null)[] }

interface Props {
  baris: Baris[];
  seri: Seri[];
  maks?: number;
  acuan?: { nilai: number; label: string };
  format: (n: number) => string;
  judulAkses: string;
}

const LEBAR = 640;
const KIRI = 150;
const KANAN = 56;
const TINGGI_BATANG = 14;
const CELAH = 2;

/** Batang horizontal (satu atau dua seri) dengan garis acuan opsional dan tooltip per batang. */
export function GrafikBatang({ baris, seri, maks, acuan, format, judulAkses }: Props) {
  const [sorot, setSorot] = useState<{ x: number; y: number; teks: string } | null>(null);
  const nilaiMaks = maks ?? Math.max(acuan?.nilai ?? 0, ...baris.flatMap((b) => b.nilai.map((v) => v ?? 0)), 1e-9);
  const lebarPlot = LEBAR - KIRI - KANAN;
  const tinggiKelompok = seri.length * TINGGI_BATANG + (seri.length - 1) * CELAH + 12;
  const tinggi = baris.length * tinggiKelompok + 24;
  const skala = (v: number) => (Math.max(v, 0) / nilaiMaks) * lebarPlot;

  return (
    <div>
      {seri.length > 1 ? (
        <div className="legenda">
          {seri.map((s) => <span key={s.nama}><i style={{ background: `var(--${s.warna})` }} />{s.nama}</span>)}
        </div>
      ) : null}
      <div style={{ position: "relative" }}>
      <svg className="chart" viewBox={`0 0 ${LEBAR} ${tinggi}`} role="img" aria-label={judulAkses}
           onMouseLeave={() => setSorot(null)}>
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <line key={t} className="grid-line" x1={KIRI + t * lebarPlot} x2={KIRI + t * lebarPlot} y1={0} y2={tinggi - 20} />
        ))}
        {baris.map((b, i) => {
          const y0 = i * tinggiKelompok + 6;
          return (
            <g key={b.label}>
              <text className="lbl" x={KIRI - 10} y={y0 + (tinggiKelompok - 12) / 2 + 4} textAnchor="end">{b.label}</text>
              {b.nilai.map((v, j) => {
                const y = y0 + j * (TINGGI_BATANG + CELAH);
                const w = v === null ? 0 : Math.max(skala(v), 2);
                const teks = `${b.label}${seri.length > 1 ? ` · ${seri[j].nama}` : ""}: ${v === null ? "tidak ada" : format(v)}`;
                return (
                  <g key={j} onMouseEnter={() => setSorot({ x: KIRI + w, y, teks })}>
                    <rect className="hit" x={KIRI} y={y - 1} width={lebarPlot} height={TINGGI_BATANG + 2} fill="transparent" />
                    <path className="mark" fill={`var(--${seri[j].warna})`}
                          d={`M${KIRI},${y} h${Math.max(w - 4, 0)} a4,4 0 0 1 4,4 v${TINGGI_BATANG - 8} a4,4 0 0 1 -4,4 h-${Math.max(w - 4, 0)} z`} />
                    {seri.length <= 2 && v !== null ? (
                      <text x={KIRI + w + 6} y={y + TINGGI_BATANG - 3}>{format(v)}</text>
                    ) : null}
                  </g>
                );
              })}
            </g>
          );
        })}
        {acuan ? (
          <g>
            <line className="ref" x1={KIRI + skala(acuan.nilai)} x2={KIRI + skala(acuan.nilai)} y1={0} y2={tinggi - 20} />
            <text x={KIRI + skala(acuan.nilai)} y={tinggi - 6} textAnchor="middle">{acuan.label}</text>
          </g>
        ) : null}
      </svg>
      {sorot ? (
        <div role="tooltip" style={{
          position: "absolute", left: `${(sorot.x / LEBAR) * 100}%`, top: `${(sorot.y / tinggi) * 100}%`,
          transform: "translate(8px, -110%)", background: "var(--ink)", color: "var(--surface)", padding: "4px 8px",
          borderRadius: 6, fontSize: 12, pointerEvents: "none", whiteSpace: "nowrap" }}>{sorot.teks}</div>
      ) : null}
      </div>
    </div>
  );
}
