import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api";
import { Chip, Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { DAFTAR_TAHAP } from "../layout/Tahapan";
import { angka, skor100 } from "../format";

export function Ringkasan() {
  const hasil = useQuery({ queryKey: ["hasil"], queryFn: api.hasil });
  const hip = useQuery({ queryKey: ["hipotesis"], queryFn: api.hipotesis });
  const data = useQuery({ queryKey: ["data"], queryFn: api.data });
  return (
    <>
      <Kepala judul="Sistem analitik ulasan restoran berbasis ABSA">
        Prototipe dibangun dengan SDLC Prototipe. Setiap halaman di kiri adalah satu tahap pada diagram penelitian, lengkap dengan buktinya.
      </Kepala>
      {data.data?.data_contoh ? <div className="peringatan">Data yang dimuat adalah <b>data contoh</b> (sintetis, benih tetap). Angka di dashboard ini belum boleh dikutip sebagai hasil penelitian.</div> : null}
      <div className="grid grid-4">
        <Stat nilai={data.data ? angka(data.data.ulasan.total) : "—"} label="Ulasan termuat" />
        <Stat nilai={data.data ? `${data.data.sampling.n} restoran` : "—"} label="Rencana sampel (purposive)" />
        <Stat nilai={hasil.data?.prioritas[0]?.label ?? "—"} label="Prioritas perbaikan pertama" />
        <Stat nilai={hasil.data?.prioritas[0] ? skor100(hasil.data.prioritas[0].priority) : "—"} label="Skor prioritas (0–100)" />
      </div>
      <Kartu judul="Alur penelitian" className="mt" sub="Klik satu tahap untuk melihat buktinya.">
        <div className="alur">
          {DAFTAR_TAHAP.slice(1).map((t, i) => (
            <Link key={t.jalur} to={t.jalur}><b>{i + 1}. {t.judul}</b><small>{t.ket}</small></Link>
          ))}
        </div>
      </Kartu>
      <Kartu judul="Keputusan hipotesis" className="mt">
        <Muat q={hip}>{(d) => (
          <table><thead><tr><th>RM</th><th>H1</th><th>Keputusan</th></tr></thead><tbody>
            {d.hipotesis.map((h) => (
              <tr key={h.rm}><td>RM{h.rm}</td><td>{h.h1}</td><td>{h.status !== "selesai" ? <Chip status="belum_tersedia" />
                : h.tolak_h0 ? <Chip status="lulus" teks="H0 ditolak" /> : <Chip status="gagal" teks="H0 tidak ditolak" />}</td></tr>
            ))}
          </tbody></table>
        )}</Muat>
      </Kartu>
    </>
  );
}
