import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { Kartu, Kepala } from "../components/Kartu";
import { Muat } from "../components/Muat";
import { angka } from "../format";

export function DesainPage() {
  const q = useQuery({ queryKey: ["desain"], queryFn: api.desain });
  return (
    <>
      <Kepala no={4} judul="Desain cepat">
        Arsitektur klien-server lima lapis. Lapis 1–4 adalah inti analitik Python; lapis 5 terdiri atas API FastAPI (5a) dan klien React (5b). Data antar-lapis mengikuti kontrak tetap.
      </Kepala>
      <Muat q={q}>{(d) => (
        <>
          <Kartu judul="Lima lapis">
            <ol style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
              {d.lapis.slice().reverse().map((l) => (
                <li key={l.no} style={{ display: "grid", gridTemplateColumns: "34px 1fr", gap: 12, alignItems: "center",
                  border: "1px solid var(--rule)", borderRadius: 8, padding: "10px 12px", background: l.no === 5 ? "var(--accent-tint)" : "var(--inset)" }}>
                  <span className="brand-mark" style={{ width: 28, height: 28 }}>L{l.no}</span>
                  <span><b>{l.nama}</b><br /><span className="mono kecil">{l.modul}</span></span>
                </li>
              ))}
            </ol>
            <p className="kecil mt">Bobot skor prioritas: {Object.entries(d.bobot).map(([k, v]) => `${k} ${angka(v, 1)}`).join(" · ")}. Aspek: {d.aspek.join(", ")}.
              Skema API lengkap: <a href="/api/v1/docs">/api/v1/docs</a>.</p>
          </Kartu>
          <div className="grid grid-2 mt">
            {d.kontrak.map((k) => (
              <Kartu key={k.nama} judul={k.nama}>
                <table><thead><tr><th>Bidang</th><th>Tipe</th></tr></thead><tbody>
                  {k.bidang.map((b) => <tr key={b.nama}><td className="mono">{b.nama}</td><td className="mono kecil">{b.tipe}</td></tr>)}
                </tbody></table>
              </Kartu>
            ))}
          </div>
        </>
      )}</Muat>
    </>
  );
}
