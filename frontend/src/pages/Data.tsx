import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { BelumTersedia } from "../components/BelumTersedia";
import { GrafikBatang } from "../components/Grafik";
import { Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka } from "../format";

export function DataPage() {
  const q = useQuery({ queryKey: ["data"], queryFn: api.data });
  return (
    <>
      <Kepala no={1} judul="Pengumpulan data">
        Ulasan publik Google Maps berbahasa Indonesia. Sampel dipilih secara purposive: urut jumlah ulasan dalam rentang tahun, paling banyak dua restoran per kategori.
      </Kepala>
      <Muat q={q}>{(d) => (
        <>
          {d.data_contoh ? <div className="peringatan">Data yang dimuat adalah data contoh (sintetis).</div> : null}
          <div className="grid grid-4">
            <Stat nilai={angka(d.kandidat)} label="Restoran kandidat aktif" />
            <Stat nilai={angka(d.sampling.n)} label="Restoran sampel" />
            <Stat nilai={`${d.sampling.rentang_tahun[0]}–${d.sampling.rentang_tahun[1]}`} label="Rentang tahun ulasan" />
            <Stat nilai={angka(d.ulasan.total)} label="Ulasan pada berkas analisis" />
          </div>
          <Kartu judul="Sampel delapan restoran" className="mt"
                 sub={<>Target per restoran = min(ulasan tersedia, {angka(d.sampling.batas_target)}). Maksimal {d.sampling.maks_per_kategori} restoran per kategori.</>}>
            {d.sampling.restoran.length === 0 ? <BelumTersedia judul="Pemilihan sampel menunggu data mentah."
              langkah={`letakkan data/raw/maps/<kode>_hasil.jsonl lalu ${d.sampling.langkah}`} /> : (
              <div className="tabel-wrap"><table>
                <thead><tr><th>Kode</th><th>Restoran</th><th>Kota</th><th>Kategori</th><th className="num">Tersedia</th><th className="num">Target</th></tr></thead>
                <tbody>{d.sampling.restoran.map((r) => (
                  <tr key={r.kode}><td className="mono">{r.kode}</td><td>{r.nama}</td><td>{r.kota}</td><td>{r.kategori}</td>
                    <td className="num">{angka(r.tersedia)}</td><td className="num">{angka(r.target)}</td></tr>
                ))}</tbody>
              </table>
              <p className="kecil">{d.sampling.ditetapkan ? "Sampel sudah ditetapkan di config/restaurants.csv." : `Usulan otomatis; tetapkan dengan ${d.sampling.langkah}.`} Target total {angka(d.sampling.target_total)} ulasan.</p></div>
            )}
          </Kartu>
          <div className="grid grid-2 mt">
            <Kartu judul="Ulasan per restoran (berkas analisis)">
              {Object.keys(d.ulasan.per_restoran).length ? (
                <GrafikBatang judulAkses="Jumlah ulasan per restoran" seri={[{ nama: "Ulasan", warna: "series-1" }]}
                  baris={Object.entries(d.ulasan.per_restoran).map(([label, n]) => ({ label: label.length > 22 ? `${label.slice(0, 21)}…` : label, nilai: [n] }))}
                  format={(n) => angka(n)} />
              ) : <BelumTersedia langkah={d.langkah} />}
            </Kartu>
            <Kartu judul="Sebaran rating bintang">
              {Object.keys(d.ulasan.rating).length ? (
                <GrafikBatang judulAkses="Jumlah ulasan per rating" seri={[{ nama: "Ulasan", warna: "series-1" }]}
                  baris={Object.entries(d.ulasan.rating).map(([r, n]) => ({ label: `${r} bintang`, nilai: [n] }))}
                  format={(n) => angka(n)} />
              ) : <BelumTersedia langkah={d.langkah} />}
            </Kartu>
          </div>
        </>
      )}</Muat>
    </>
  );
}
