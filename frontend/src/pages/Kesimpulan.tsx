import { Fragment } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type Hipotesis } from "../api";
import { BelumTersedia } from "../components/BelumTersedia";
import { Chip, Kartu, Kepala } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka } from "../format";

const RM = {
  1: "Rancangan arsitektur lima lapis, katalog kebutuhan, dan kontrak antar-lapis",
  2: "Kelulusan uji perangkat lunak dan waktu proses per 1.000 ulasan",
  3: "Kesesuaian peringkat prioritas dengan urutan pakar",
} as const;

function nilai(v: unknown): string {
  if (typeof v === "number") return angka(v, Number.isInteger(v) ? 0 : 3);
  if (Array.isArray(v)) return v.length ? v.join(", ") : "tidak ada";
  if (v === null || v === undefined) return "—";
  return String(v);
}

export function KartuHipotesis({ h }: { h: Hipotesis }) {
  const kelas = h.tolak_h0 === null ? "" : h.tolak_h0 ? "tolak" : "tidak";
  return (
    <Kartu className={`h-kartu ${kelas}`} judul={`RM${h.rm} · ${RM[h.rm as 1 | 2 | 3]}`}>
      <div style={{ marginBottom: 10 }}>
        {h.status !== "selesai" ? <Chip status="belum_tersedia" />
          : h.tolak_h0 ? <Chip status="lulus" teks="H0 ditolak · H1 diterima" /> : <Chip status="gagal" teks="H0 tidak ditolak" />}
      </div>
      <dl className="dl">
        <dt>H0</dt><dd>{h.h0}</dd><dt>H1</dt><dd>{h.h1}</dd>
        {h.p !== null ? <><dt>p</dt><dd className="mono">{angka(h.p, 4)}</dd></> : null}
        {h.statistik ? Object.entries(h.statistik).map(([k, v]) => (
          <Fragment key={k}><dt>{k.replaceAll("_", " ")}</dt><dd className="mono">{nilai(v)}</dd></Fragment>
        )) : null}
      </dl>
      {h.status !== "selesai" ? <div className="mt"><BelumTersedia langkah={h.langkah} /></div> : null}
      {h.status === "selesai" && !h.tolak_h0 ? <p className="kecil mt">Rekomendasi: {h.rekomendasi}</p> : null}
    </Kartu>
  );
}

export function KesimpulanPage() {
  const q = useQuery({ queryKey: ["hipotesis"], queryFn: api.hipotesis });
  return (
    <>
      <Kepala no={9} judul="Analisis hasil dan penarikan kesimpulan">
        Setiap rumusan masalah diputuskan dari bukti yang benar-benar ada, dengan α = 0,05. Bila bukti belum ada, keputusan tidak ditebak.
      </Kepala>
      <Muat q={q}>{(d) => <div className="grid">{d.hipotesis.map((h) => <KartuHipotesis key={h.rm} h={h} />)}</div>}</Muat>
    </>
  );
}
