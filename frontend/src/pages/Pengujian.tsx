import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { BelumTersedia } from "../components/BelumTersedia";
import { GrafikBatang } from "../components/Grafik";
import { Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka } from "../format";

export function PengujianPage() {
  const q = useQuery({ queryKey: ["pengujian"], queryFn: api.pengujian });
  return (
    <>
      <Kepala no={7} judul="Pengujian perangkat lunak">
        Uji unit, integrasi, dan sistem dengan pytest dan Playwright, serta pengujian non-fungsional KNF-01 sampai KNF-05. Uji kritis adalah seluruh kasus yang terpetakan ke FR.
      </Kepala>
      <Muat q={q}>{(d) => (
        <>
          {d.junit ? (
            <div className="grid grid-4">
              <Stat nilai={angka(d.junit.total)} label="Uji dijalankan" />
              <Stat nilai={angka(d.junit.lulus)} label="Lulus" />
              <Stat nilai={angka(d.junit.gagal)} label="Gagal" />
              <Stat nilai={angka(d.junit.dilewati)} label="Dilewati" />
            </div>
          ) : <BelumTersedia langkah={d.langkah} />}
          <Kartu judul="Kasus uji otomatis per tingkat" className="mt">
            <table><thead><tr><th>Tingkat</th><th className="num">Lulus</th><th className="num">Gagal</th><th className="num">Belum dijalankan</th></tr></thead>
              <tbody>{Object.entries(d.per_tingkat).map(([t, n]) => (
                <tr key={t}><td style={{ textTransform: "capitalize" }}>{t}</td><td className="num">{angka(n.lulus ?? 0)}</td>
                  <td className="num">{angka(n.gagal ?? 0)}</td><td className="num">{angka((n.belum_dijalankan ?? 0) + (n.dilewati ?? 0))}</td></tr>
              ))}</tbody></table>
          </Kartu>
          <Kartu judul="KNF-01 · waktu analisis per 1.000 ulasan" className="mt" sub="Batas 60 detik; lima ulangan.">
            {d.benchmark ? (() => {
              const n = Math.max(d.benchmark.summary.n_ulasan ?? 1, 1);
              return (
                <GrafikBatang judulAkses="Waktu analisis per 1.000 ulasan tiap ulangan" seri={[{ nama: "Detik per 1.000 ulasan", warna: "series-1" }]}
                  acuan={{ nilai: 60, label: "batas 60 s" }}
                  baris={d.benchmark.perulangan.map((u) => ({ label: `Ulangan ${u.ulangan}`, nilai: [(u.total_dinding * 1000) / n] }))}
                  format={(v) => `${angka(v, 2)} s`} />
              );
            })() : <BelumTersedia langkah="python -m rra.cli benchmark --repeat 5" />}
          </Kartu>
        </>
      )}</Muat>
    </>
  );
}
