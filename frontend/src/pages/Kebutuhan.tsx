import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { Chip, Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { BelumTersedia } from "../components/BelumTersedia";
import { angka } from "../format";

export function KebutuhanPage() {
  const q = useQuery({ queryKey: ["kebutuhan"], queryFn: api.kebutuhan });
  return (
    <>
      <Kepala no={3} judul="Analisis kebutuhan">
        Katalog kebutuhan fungsional (FR) dan non-fungsional (KNF). Setiap kebutuhan dipetakan ke kasus uji; status kasus dibaca dari laporan pytest dan berkas bukti manual.
      </Kepala>
      <Muat q={q}>{(d) => {
        const kasus = new Map(d.kasus.map((k) => [k.kode, k]));
        const lulus = d.kasus.filter((k) => k.hasil === "lulus").length;
        return (
          <>
            <div className="grid grid-3">
              <Stat nilai={`${angka(d.persen_terlacak, 0)}%`} label="Kebutuhan terlacak ke kasus uji" />
              <Stat nilai={angka(d.kebutuhan.length)} label="Kebutuhan (8 FR, 5 KNF)" />
              <Stat nilai={`${angka(lulus)}/${angka(d.kasus.length)}`} label="Kasus uji lulus" />
            </div>
            {!d.junit_tersedia ? <div className="mt"><BelumTersedia judul="Status kasus otomatis belum ada." langkah={d.langkah} /></div> : null}
            <Kartu judul="Matriks keterlacakan" className="mt">
              <div className="tabel-wrap"><table>
                <thead><tr><th>Kode</th><th>Kebutuhan</th><th>Kriteria lulus</th><th>Kasus uji</th></tr></thead>
                <tbody>{d.kebutuhan.map((k) => (
                  <tr key={k.kode}><td className="mono">{k.kode}</td><td>{k.uraian}</td><td className="kecil">{k.kriteria}</td>
                    <td><div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>{k.kasus.map((c) => (
                      <span key={c} title={kasus.get(c)?.nama}><Chip status={kasus.get(c)?.hasil ?? "belum_dijalankan"} teks={c} /></span>
                    ))}</div></td></tr>
                ))}</tbody>
              </table></div>
            </Kartu>
            <Kartu judul="Kasus uji" className="mt">
              <div className="tabel-wrap"><table>
                <thead><tr><th>Kode</th><th>Tingkat</th><th>Yang diuji</th><th>Berkas / bukti</th><th>Jenis</th><th>Hasil</th></tr></thead>
                <tbody>{d.kasus.map((c) => (
                  <tr key={c.kode}><td className="mono">{c.kode}</td><td>{c.tingkat}</td><td>{c.nama}{c.kritis ? <span className="kecil"> · kritis</span> : null}</td>
                    <td className="mono kecil">{c.berkas ?? c.bukti}</td><td>{c.jenis}</td><td><Chip status={c.hasil} /></td></tr>
                ))}</tbody>
              </table></div>
            </Kartu>
          </>
        );
      }}</Muat>
    </>
  );
}
