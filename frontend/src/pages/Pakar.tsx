import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { BelumTersedia } from "../components/BelumTersedia";
import { GrafikBatang } from "../components/Grafik";
import { Kartu, Kepala, Stat } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka } from "../format";

export function PakarPage() {
  const q = useQuery({ queryKey: ["pakar"], queryFn: api.pakar });
  return (
    <>
      <Kepala no={8} judul="Validasi pakar">
        Urutan lima aspek dari sistem dibandingkan dengan urutan pakar per restoran memakai ρ Spearman. Median ρ diuji terhadap 0,60 dengan Wilcoxon satu sampel satu sisi (α = 0,05). Dengan delapan restoran, nilai p terkecil yang mungkin adalah 1/256.
      </Kepala>
      <Muat q={q}>{(d) => d.status !== "selesai" || !d.uji_median || !d.rho_per_restoran ? <BelumTersedia langkah={d.langkah} /> : (
        <>
          <div className="grid grid-4">
            <Stat nilai={angka(d.uji_median.n)} label="Restoran dinilai" />
            <Stat nilai={d.uji_median.median === null ? "—" : angka(d.uji_median.median, 2)} label="Median ρ" />
            <Stat nilai={d.uji_median.p === null ? "—" : angka(d.uji_median.p, 4)} label="p (Wilcoxon, satu sisi)" />
            <Stat nilai={`${angka((d.kesesuaian_peringkat_1 ?? 0) * 100, 0)}%`} label="Peringkat 1 sama dengan pakar" />
          </div>
          <Kartu judul="ρ Spearman per restoran" className="mt" sub="Garis putus-putus: ambang 0,60.">
            <GrafikBatang judulAkses="Korelasi Spearman per restoran" seri={[{ nama: "ρ", warna: "series-1" }]} maks={1}
              acuan={{ nilai: 0.6, label: "0,60" }}
              baris={Object.entries(d.rho_per_restoran).map(([r, v]) => ({ label: r.length > 22 ? `${r.slice(0, 21)}…` : r, nilai: [v] }))}
              format={(v) => angka(v, 2)} />
          </Kartu>
        </>
      )}</Muat>
    </>
  );
}
