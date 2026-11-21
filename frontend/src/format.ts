const pemformat = new Map<number, Intl.NumberFormat>();

export function angka(nilai: number | null | undefined, desimal = 0): string {
  if (nilai === null || nilai === undefined || Number.isNaN(nilai)) return "—";
  let f = pemformat.get(desimal);
  if (!f) {
    f = new Intl.NumberFormat("id-ID", { minimumFractionDigits: desimal, maximumFractionDigits: desimal });
    pemformat.set(desimal, f);
  }
  return f.format(nilai);
}

/** Skor prioritas internal 0–1 ditampilkan pada skala 0–100, satu desimal. */
export function skor100(nilai: number): string {
  return angka(nilai * 100, 1);
}

export function waktu(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("id-ID", { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso));
}
