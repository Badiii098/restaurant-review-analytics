import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { BelumTersedia } from "../components/BelumTersedia";
import { Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka } from "../format";

export function AnotasiPage() {
  const q = useQuery({ queryKey: ["anotasi"], queryFn: api.anotasi });
  return (
    <>
      <Kepala no={2} judul="Anotasi data">
        Dua anotator melabeli 500 ulasan yang sama secara terpisah (aspek dan sentimen). Kesepakatan diukur dengan κ Cohen; tafsiran mengikuti Landis &amp; Koch (1977).
      </Kepala>
      <Muat q={q}>{(d) => (
        <>
          <div className="grid grid-3">
            <Stat nilai={angka(d.berlabel)} label="Ulasan berlabel" />
            <Stat nilai={angka(d.target)} label="Target anotasi" />
            <Stat nilai={`${angka(d.progres, 1)}%`} label="Progres terhadap target" />
          </div>
          <Kartu judul="Progres anotasi" className="mt">
            <div className="progres" role="progressbar" aria-valuenow={d.progres} aria-valuemin={0} aria-valuemax={100}>
              <div style={{ width: `${d.progres}%` }} /></div>
          </Kartu>
          <Kartu judul="Kesepakatan antar-anotator (κ Cohen)" className="mt">
            {d.status !== "selesai" || !d.kappa ? <BelumTersedia langkah={d.langkah} /> : (
              <table><thead><tr><th>Tingkat</th><th className="num">n</th><th className="num">Kesepakatan teramati</th><th className="num">κ</th><th>Tafsiran</th></tr></thead>
                <tbody>{[d.kappa.aspek, d.kappa.sentimen].map((k) => (
                  <tr key={k.tingkat}><td style={{ textTransform: "capitalize" }}>{k.tingkat}</td><td className="num">{angka(k.n)}</td>
                    <td className="num">{k.kesepakatan_teramati !== undefined ? angka(k.kesepakatan_teramati, 3) : "—"}</td>
                    <td className="num"><b>{angka(k.kappa, 3)}</b></td><td>{k.tafsiran}</td></tr>
                ))}</tbody></table>
            )}
          </Kartu>
        </>
      )}</Muat>
    </>
  );
}
