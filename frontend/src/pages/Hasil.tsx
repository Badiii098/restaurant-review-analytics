import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type Frasa, type Prioritas, type Rekomendasi } from "../api";
import { BelumTersedia } from "../components/BelumTersedia";
import { Chip, Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka, skor100, waktu } from "../format";

export function TabelPrioritas({ prioritas }: { prioritas: Prioritas[] }) {
  return (
    <div className="tabel-wrap">
      <table>
        <thead>
          <tr><th className="num">#</th><th>Aspek layanan</th><th className="num">Ulasan negatif</th>
            <th>Skor prioritas</th><th className="num">Nilai</th></tr>
        </thead>
        <tbody>
          {prioritas.map((p) => (
            <tr key={p.aspect}>
              <td className="num">{p.rank}</td>
              <td><b>{p.label}</b><div className="kecil">volume {angka(p.volume, 2)} · keparahan {angka(p.severity, 2)} · keragaman {angka(p.diversity, 2)}</div></td>
              <td className="num">{angka(p.n_negative)}<div className="kecil">dari {angka(p.n_total)}</div></td>
              <td style={{ width: "32%" }}><div className="bar-track" title={`${p.label}: ${skor100(p.priority)}`}>
                <div className="bar-fill" style={{ width: `${p.priority * 100}%` }} /></div></td>
              <td className="num"><b>{skor100(p.priority)}</b></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function kelompok(frasa: Frasa[]): [string, Frasa[]][] {
  const peta = new Map<string, Frasa[]>();
  for (const f of frasa) peta.set(f.aspect, [...(peta.get(f.aspect) ?? []), f]);
  return [...peta.entries()];
}

/** Dua tindakan teratas per aspek; sisanya dapat dibuka. */
function TabelRekomendasi({ daftar }: { daftar: Rekomendasi[] }) {
  const [semua, setSemua] = useState(false);
  const hitung = new Map<string, number>();
  const tampil = semua ? daftar : daftar.filter((r) => {
    const n = (hitung.get(r.aspect) ?? 0) + 1;
    hitung.set(r.aspect, n);
    return n <= 2;
  });
  return (
    <>
      <div className="tabel-wrap"><table><thead><tr><th>Aspek</th><th>Pemicu</th><th>Tindakan</th></tr></thead><tbody>
        {tampil.map((r, i) => (
          <tr key={i}><td style={{ textTransform: "capitalize" }}>{r.aspect}</td><td>{r.phrase}</td><td>{r.action}</td></tr>
        ))}
      </tbody></table></div>
      {daftar.length > tampil.length || semua ? (
        <button className="tombol garis mt" onClick={() => setSemua((s) => !s)}>
          {semua ? "Ringkas" : `Tampilkan semua (${daftar.length})`}</button>
      ) : null}
    </>
  );
}

export function HasilPage() {
  const q = useQuery({ queryKey: ["hasil"], queryFn: api.hasil });
  const sens = useQuery({ queryKey: ["sensitivitas"], queryFn: api.sensitivitas });
  const klien = useQueryClient();
  const ulang = useMutation({ mutationFn: api.analisis, onSuccess: () => klien.invalidateQueries() });
  return (
    <>
      <Kepala no={6} judul="Hasil & prioritas perbaikan">
        Skor prioritas = 0,4·Volume + 0,4·Keparahan + 0,2·Keragaman, ditampilkan pada skala 0–100. Setiap komponen tersimpan sebagai bahan audit.
      </Kepala>
      <Muat q={q}>{(d) => d.status !== "selesai" || !d.run ? <BelumTersedia langkah={d.langkah} /> : (
        <>
          <div className="grid grid-4">
            <Stat nilai={angka(d.run.n_reviews)} label="Ulasan dianalisis" />
            <Stat nilai={d.prioritas[0]?.label ?? "—"} label="Prioritas pertama" />
            <Stat nilai={d.prioritas[0] ? skor100(d.prioritas[0].priority) : "—"} label="Skor tertinggi (0–100)" />
            <Stat nilai={`${angka(Object.values(d.run.timings).reduce((a, b) => a + b, 0), 2)} s`} label="Waktu komputasi" />
          </div>
          <Kartu judul="Peringkat prioritas" className="mt"
                 sub={<>Hasil nomor {d.run.run_id} · {waktu(d.run.created_at)} · model {d.run.model_name.toUpperCase()}</>}>
            <TabelPrioritas prioritas={d.prioritas} />
            <div style={{ marginTop: 14, display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <button className="tombol" disabled={ulang.isPending} onClick={() => ulang.mutate()}>
                {ulang.isPending ? "Menghitung ulang…" : "Hitung ulang analisis"}</button>
              {ulang.isError ? <span className="galat">{(ulang.error as Error).message}</span> : null}
              {ulang.isSuccess ? <span className="kecil">Hasil nomor {ulang.data.run_id} tersimpan.</span> : null}
            </div>
          </Kartu>
          <div className="grid grid-2 mt">
            <Kartu judul="Frasa keluhan dominan" sub="Frekuensi kemunculan per aspek; dapat ditelusuri ke ulasan contoh.">
              <div className="tabel-wrap"><table><thead><tr><th>Aspek</th><th>Frasa teratas</th></tr></thead><tbody>
                {kelompok(d.frasa).map(([aspek, daftar]) => (
                  <tr key={aspek}><td style={{ textTransform: "capitalize" }}>{aspek}</td>
                    <td>{daftar.slice(0, 3).map((f) => `${f.phrase} (${angka(f.frequency)})`).join(" · ")}</td></tr>
                ))}
              </tbody></table></div>
            </Kartu>
            <Kartu judul="Tindakan yang disarankan" sub="Dari tabel aturan DINESERV, bukan keluaran model.">
              <TabelRekomendasi daftar={d.rekomendasi} />
            </Kartu>
          </div>
          <Kartu judul="Uji sensitivitas bobot ±10%" className="mt" sub="Apakah peringkat pertama bertahan saat satu bobot digeser?">
            <Muat q={sens}>{(s) => s.status !== "selesai" ? <BelumTersedia langkah={s.langkah} /> : (
              <div className="tabel-wrap"><table>
                <thead><tr><th>Komponen</th><th>Arah</th><th>Peringkat</th><th className="num">τ Kendall</th><th>Peringkat 1</th></tr></thead>
                <tbody>{s.skenario.map((r) => (
                  <tr key={r.komponen + r.arah}><td>{r.komponen}</td><td>{r.arah}10%</td><td>{r.peringkat.join(" › ")}</td>
                    <td className="num">{angka(r.tau_kendall, 2)}</td>
                    <td><Chip status={r.peringkat_1_sama ? "lulus" : "gagal"} teks={r.peringkat_1_sama ? "Sama" : "Berubah"} /></td></tr>
                ))}</tbody>
              </table></div>
            )}</Muat>
          </Kartu>
        </>
      )}</Muat>
    </>
  );
}
