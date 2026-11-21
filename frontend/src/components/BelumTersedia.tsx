export function BelumTersedia({ langkah, judul }: { langkah?: string | null; judul?: string }) {
  return (
    <div className="belum" role="status">
      <b>{judul ?? "Bukti belum tersedia."}</b>{" "}
      {judul ? "Langkah berikutnya:" : "Angka tidak ditampilkan sampai sumbernya dibuat. Jalankan:"}
      {langkah ? <code>{langkah}</code> : null}
    </div>
  );
}
