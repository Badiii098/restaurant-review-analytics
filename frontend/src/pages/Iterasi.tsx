import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { BelumTersedia } from "../components/BelumTersedia";
import { GrafikBatang, type Seri } from "../components/Grafik";
import { Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka, waktu } from "../format";

const ASPEK = ["makanan", "pelayanan", "harga", "suasana", "fasilitas"];
const WARNA: Seri["warna"][] = ["series-1", "series-2"];

function tanda(n: number): string {
  return `${n > 0 ? "+" : ""}${angka(n, 4)}`;
}

export function IterasiPage() {
  const q = useQuery({ queryKey: ["iterasi"], queryFn: api.iterasi });
  return (
    <>
      <Kepala no={5} judul="Pembangunan prototipe dan evaluasi (iterasi 1–2)">
        Komponen NLP: TF-IDF (n-gram 1–2) + SVM linear. Setiap iterasi dievaluasi dengan Macro-F1 validasi silang; temuan evaluasi menjadi bahan perbaikan iterasi berikutnya.
      </Kepala>
      <Muat q={q}>{(d) => d.status !== "selesai" ? <BelumTersedia langkah={d.langkah} /> : (
        <>
          {d.iterasi.some((i) => i.data_contoh) ? <div className="peringatan">Sebagian iterasi dihitung dari data contoh, bukan data berlabel penelitian.</div> : null}
          <div className="grid grid-4">
            {d.iterasi.slice(-2).flatMap((i) => [
              <Stat key={`a${i.nomor}`} nilai={angka(i.ringkasan.aspect_macro_f1_mean, 3)} label={`Macro-F1 aspek · iterasi ${i.nomor}`} />,
              <Stat key={`s${i.nomor}`} nilai={angka(i.ringkasan.sentiment_macro_f1_mean, 3)} label={`Macro-F1 sentimen · iterasi ${i.nomor}`} />,
            ])}
          </div>
          {d.selisih ? (
            <Kartu judul="Selisih iterasi terakhir terhadap iterasi pertama" className="mt">
              <p style={{ margin: 0 }}>Macro-F1 aspek <b className="mono">{tanda(d.selisih.aspek_macro_f1)}</b> · Macro-F1 sentimen <b className="mono">{tanda(d.selisih.sentimen_macro_f1)}</b></p>
            </Kartu>
          ) : <div className="mt"><BelumTersedia judul="Baru ada satu iterasi."
               langkah={'python -m rra.cli evaluate --iterasi 2 --catatan "<perbaikan yang dilakukan>"'} /></div>}
          <Kartu judul="F1 per aspek" className="mt" sub="Rerata antar-lipatan validasi silang.">
            <GrafikBatang judulAkses="F1 per aspek untuk tiap iterasi" maks={1}
              seri={d.iterasi.slice(-2).map((i, j) => ({ nama: `Iterasi ${i.nomor}`, warna: WARNA[j] }))}
              baris={ASPEK.map((a) => ({ label: a, nilai: d.iterasi.slice(-2).map((i) => i.per_aspek_f1[a] ?? null) }))}
              format={(n) => angka(n, 3)} />
          </Kartu>
          <Kartu judul="Catatan iterasi" className="mt">
            <table><thead><tr><th>Iterasi</th><th>Waktu</th><th>Commit</th><th>Catatan perbaikan</th><th className="num">Aspek (± sd)</th><th className="num">Sentimen (± sd)</th></tr></thead>
              <tbody>{d.iterasi.map((i) => (
                <tr key={i.nomor}><td>{i.nomor}</td><td>{waktu(i.waktu)}</td><td className="mono">{i.commit ?? "—"}</td><td>{i.catatan || "—"}</td>
                  <td className="num">{angka(i.ringkasan.aspect_macro_f1_mean, 3)} ± {angka(i.ringkasan.aspect_macro_f1_std, 3)}</td>
                  <td className="num">{angka(i.ringkasan.sentiment_macro_f1_mean, 3)} ± {angka(i.ringkasan.sentiment_macro_f1_std, 3)}</td></tr>
              ))}</tbody></table>
          </Kartu>
        </>
      )}</Muat>
    </>
  );
}
