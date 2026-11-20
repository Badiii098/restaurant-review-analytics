import { NavLink } from "react-router-dom";

/** Urutan halaman mengikuti diagram tahapan penelitian (Gambar 3.1). */
export const DAFTAR_TAHAP = [
  { jalur: "/", judul: "Ringkasan", ket: "alur & keputusan" },
  { jalur: "/data", judul: "Pengumpulan Data", ket: "8 restoran" },
  { jalur: "/anotasi", judul: "Anotasi Data", ket: "500 ulasan, kappa" },
  { jalur: "/kebutuhan", judul: "Analisis Kebutuhan", ket: "FR, KNF" },
  { jalur: "/desain", judul: "Desain Cepat", ket: "arsitektur, kontrak" },
  { jalur: "/iterasi", judul: "Prototipe & Iterasi", ket: "Macro-F1, iterasi 1–2" },
  { jalur: "/hasil", judul: "Hasil & Prioritas", ket: "skor 0–100" },
  { jalur: "/pengujian", judul: "Pengujian", ket: "unit, integrasi, sistem" },
  { jalur: "/pakar", judul: "Validasi Pakar", ket: "Spearman, Wilcoxon" },
  { jalur: "/kesimpulan", judul: "Kesimpulan", ket: "H1–H3" },
] as const;

export function Tahapan({ onPilih }: { onPilih?: () => void }) {
  return (
    <nav aria-label="Tahapan penelitian">
      <p className="tahap-label">Tahapan penelitian</p>
      <ol className="tahapan">
        {DAFTAR_TAHAP.map((t, i) => (
          <li key={t.jalur}>
            <NavLink to={t.jalur} end={t.jalur === "/"} onClick={onPilih}>
              <span className="no" aria-hidden>{i === 0 ? "★" : i}</span>
              <span>{t.judul}</span>
            </NavLink>
          </li>
        ))}
      </ol>
    </nav>
  );
}
