import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Tahapan, DAFTAR_TAHAP } from "./Tahapan";

test("navigasi menampilkan sepuluh halaman urut diagram penelitian", () => {
  render(<MemoryRouter><Tahapan /></MemoryRouter>);
  const tautan = screen.getAllByRole("link").map((a) => a.textContent ?? "");
  expect(tautan).toHaveLength(10);
  expect(DAFTAR_TAHAP.map((t) => t.judul)).toEqual([
    "Ringkasan", "Pengumpulan Data", "Anotasi Data", "Analisis Kebutuhan", "Desain Cepat",
    "Prototipe & Iterasi", "Hasil & Prioritas", "Pengujian", "Validasi Pakar", "Kesimpulan",
  ]);
  expect(tautan[1]).toContain("Pengumpulan Data");
});
