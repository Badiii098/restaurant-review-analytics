import type { ReactNode } from "react";

export function Kartu({ judul, sub, children, className }: { judul?: string; sub?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`kartu ${className ?? ""}`}>
      {judul ? <h2>{judul}</h2> : null}
      {sub ? <p className="sub">{sub}</p> : null}
      {children}
    </section>
  );
}

export function Stat({ nilai, label }: { nilai: ReactNode; label: string }) {
  return <div className="kartu stat"><b>{nilai}</b><span>{label}</span></div>;
}

export function Kepala({ no, judul, children }: { no?: number; judul: string; children?: ReactNode }) {
  return (
    <header className="kepala">
      <div className="eyebrow">{no ? `Tahap ${no}` : "Prototipe SDLC"}</div>
      <h1>{judul}</h1>
      {children ? <p>{children}</p> : null}
    </header>
  );
}

const LABEL: Record<string, string> = {
  lulus: "Lulus", gagal: "Gagal", dilewati: "Dilewati", belum_dijalankan: "Belum dijalankan",
  belum_diuji: "Belum diuji", ada_bukti: "Ada bukti", selesai: "Selesai", belum_tersedia: "Belum tersedia",
};

export function Chip({ status, teks }: { status: string; teks?: string }) {
  const kelas = status === "lulus" || status === "selesai" || status === "ada_bukti" ? "lulus"
    : status === "gagal" ? "gagal" : status.startsWith("belum") ? "tunggu" : "netral";
  const ikon = kelas === "lulus" ? "✓" : kelas === "gagal" ? "✕" : kelas === "tunggu" ? "○" : "–";
  return <span className={`chip ${kelas}`}><span aria-hidden>{ikon}</span>{teks ?? LABEL[status] ?? status}</span>;
}
