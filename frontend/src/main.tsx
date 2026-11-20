import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./styles/app.css";
import { Shell } from "./layout/Shell";
import { Ringkasan } from "./pages/Ringkasan";
import { DataPage } from "./pages/Data";
import { AnotasiPage } from "./pages/Anotasi";
import { KebutuhanPage } from "./pages/Kebutuhan";
import { DesainPage } from "./pages/Desain";
import { IterasiPage } from "./pages/Iterasi";
import { HasilPage } from "./pages/Hasil";
import { PengujianPage } from "./pages/Pengujian";
import { PakarPage } from "./pages/Pakar";
import { KesimpulanPage } from "./pages/Kesimpulan";

const klien = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={klien}>
      <BrowserRouter>
        <Routes>
          <Route element={<Shell />}>
            <Route index element={<Ringkasan />} />
            <Route path="data" element={<DataPage />} />
            <Route path="anotasi" element={<AnotasiPage />} />
            <Route path="kebutuhan" element={<KebutuhanPage />} />
            <Route path="desain" element={<DesainPage />} />
            <Route path="iterasi" element={<IterasiPage />} />
            <Route path="hasil" element={<HasilPage />} />
            <Route path="pengujian" element={<PengujianPage />} />
            <Route path="pakar" element={<PakarPage />} />
            <Route path="kesimpulan" element={<KesimpulanPage />} />
            <Route path="*" element={<p>Halaman tidak ditemukan.</p>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);
