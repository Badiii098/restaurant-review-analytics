import { useState } from "react";
import { Outlet } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { Tahapan } from "./Tahapan";

export function Shell() {
  const [buka, setBuka] = useState(false);
  const status = useQuery({ queryKey: ["status"], queryFn: api.status });
  return (
    <div className="shell">
      <aside className={`sidebar ${buka ? "" : "tertutup"}`}>
        <div className="brand">
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <div className="brand-mark" aria-hidden>RRA</div>
            <div><b>Analitik Ulasan Restoran</b><span>ABSA · SDLC Prototipe</span></div>
          </div>
          <button className="tombol garis menu-toggle" onClick={() => setBuka((b) => !b)} aria-expanded={buka}>
            {buka ? "Tutup" : "Menu"}
          </button>
        </div>
        <Tahapan onPilih={() => setBuka(false)} />
        <div className="sidebar-foot">
          {status.data ? (
            <>Model {status.data.model?.toUpperCase()} · hasil nomor {status.data.hasil_terakhir ?? "—"}<br />
              Basis data <code>{status.data.basis_data}</code> · v{status.data.versi}</>
          ) : "Menghubungi API…"}
        </div>
      </aside>
      <main className="konten"><Outlet /></main>
    </div>
  );
}
