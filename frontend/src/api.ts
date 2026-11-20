/** Klien bertipe untuk API lapis 5a (/api/v1). Bentuk mengikuti src/rra/services/tahap.py. */

export type Status = "selesai" | "belum_tersedia";

export interface Belum { status: Status; langkah?: string | null }

export interface Prioritas {
  aspect: string; label: string; rank: number; priority: number;
  volume: number; severity: number; diversity: number; n_negative: number; n_total: number;
}
export interface Frasa {
  aspect: string; rank: number; phrase: string; frequency: number;
  tfidf_weight: number; score: number; example_review_ids: string[];
}
export interface Rekomendasi { aspect: string; phrase: string; action: string; evidence: string }
export interface Hasil extends Belum {
  run: { run_id: number; created_at: string; model_name: string; n_reviews: number;
         weights: Record<string, number>; timings: Record<string, number> } | null;
  prioritas: Prioritas[]; frasa: Frasa[]; rekomendasi: Rekomendasi[];
}
export interface TahapInfo { kode: string; nama: string; keterangan: string }
export interface StatusSistem extends Belum {
  versi: string; model: string; basis_data: string; hasil_terakhir: number | null; tahapan: TahapInfo[];
}
export interface SampelRestoran { kode: string; nama: string; kota: string; kategori: string; tersedia: number | null; target: number | null }
export interface Data extends Belum {
  data_contoh: boolean; kandidat: number;
  sampling: { n: number; teknik: string; rentang_tahun: number[]; batas_target: number; maks_per_kategori: number;
              ditetapkan: boolean; restoran: SampelRestoran[]; target_total: number; langkah: string };
  ulasan: { total: number; per_restoran: Record<string, number>; rating: Record<string, number>; tahun: Record<string, number> };
}
export interface KappaTingkat { tingkat: string; n: number; kappa: number; tafsiran: string; kesepakatan_teramati?: number }
export interface Anotasi extends Belum {
  target: number; berlabel: number; progres: number;
  kappa?: { aspek: KappaTingkat; sentimen: KappaTingkat };
}
export interface Kebutuhan { kode: string; uraian: string; kriteria: string; kasus: string[] }
export interface Kasus { kode: string; nama: string; tingkat: string; jenis: string; kritis: boolean;
  berkas?: string; bukti?: string; hasil: string }
export interface KatalogKebutuhan extends Belum {
  persen_terlacak: number; junit_tersedia: boolean; kebutuhan: Kebutuhan[]; kasus: Kasus[];
}
export interface Desain extends Belum {
  lapis: { no: number; nama: string; modul: string }[];
  kontrak: { nama: string; bidang: { nama: string; tipe: string }[] }[];
  aspek: string[]; bobot: Record<string, number>;
}
export interface Iterasi {
  nomor: number; waktu: string; commit: string | null; data_contoh: boolean; catatan: string;
  ringkasan: { aspect_macro_f1_mean: number; aspect_macro_f1_std: number;
               sentiment_macro_f1_mean: number; sentiment_macro_f1_std: number };
  per_aspek_f1: Record<string, number>;
}
export interface DaftarIterasi extends Belum {
  iterasi: Iterasi[]; selisih?: { aspek_macro_f1: number; sentimen_macro_f1: number } | null;
}
export interface Skenario { komponen: string; arah: string; bobot: Record<string, number>; peringkat: string[];
  peringkat_1_sama: boolean; tau_kendall: number }
export interface Sensitivitas extends Belum { skenario: Skenario[]; peringkat_1_stabil?: boolean }
export interface Pengujian extends Belum {
  junit: { total: number; lulus: number; gagal: number; dilewati: number; per_kasus: Record<string, string> } | null;
  per_tingkat: Record<string, Record<string, number>>;
  benchmark: { summary: Record<string, number>; perulangan: Record<string, number>[] } | null;
}
export interface Pakar extends Belum {
  rho_per_restoran?: Record<string, number | null>;
  uji_median?: { n: number; median: number | null; statistik: number | null; p: number | null; tolak_h0: boolean };
  kesesuaian_peringkat_1?: number; peringkat_sistem?: Record<string, string[]>;
}
export interface Hipotesis extends Belum {
  rm: number; h0: string; h1: string; rekomendasi: string; p: number | null;
  statistik: Record<string, unknown> | null; tolak_h0: boolean | null;
}
export interface DaftarHipotesis extends Belum { hipotesis: Hipotesis[] }

async function ambil<T>(jalur: string, init?: RequestInit): Promise<T> {
  const respons = await fetch(`/api/v1/${jalur}`, init);
  if (!respons.ok) {
    const isi = await respons.json().catch(() => ({}));
    throw new Error(isi.detail ?? `Permintaan ${jalur} gagal (${respons.status})`);
  }
  return respons.json() as Promise<T>;
}

export const api = {
  status: () => ambil<StatusSistem>("status"),
  data: () => ambil<Data>("data"),
  anotasi: () => ambil<Anotasi>("anotasi"),
  kebutuhan: () => ambil<KatalogKebutuhan>("kebutuhan"),
  desain: () => ambil<Desain>("desain"),
  iterasi: () => ambil<DaftarIterasi>("iterasi"),
  hasil: () => ambil<Hasil>("hasil/terakhir"),
  sensitivitas: () => ambil<Sensitivitas>("sensitivitas"),
  pengujian: () => ambil<Pengujian>("pengujian"),
  pakar: () => ambil<Pakar>("pakar"),
  hipotesis: () => ambil<DaftarHipotesis>("hipotesis"),
  analisis: () => ambil<{ run_id: number }>("analisis", { method: "POST" }),
};
