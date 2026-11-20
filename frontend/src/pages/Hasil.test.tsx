import { render, screen, within } from "@testing-library/react";
import { TabelPrioritas } from "./Hasil";
import type { Prioritas } from "../api";

const baris: Prioritas[] = [
  ["pelayanan", "Pelayanan", 0.8216], ["makanan", "Makanan", 0.4639], ["suasana", "Suasana", 0.4202],
  ["harga", "Harga", 0.3627], ["fasilitas", "Fasilitas", 0.2054],
].map(([aspect, label, priority], i) => ({
  aspect: aspect as string, label: label as string, rank: i + 1, priority: priority as number,
  volume: 0.5, severity: 0.5, diversity: 0.5, n_negative: 100, n_total: 400,
}));

test("tabel prioritas merender lima aspek berurutan dengan skor 0–100", () => {
  render(<TabelPrioritas prioritas={baris} />);
  const rows = screen.getAllByRole("row").slice(1);
  expect(rows).toHaveLength(5);
  expect(within(rows[0]).getByText("Pelayanan")).toBeInTheDocument();
  expect(within(rows[0]).getByText("82,2")).toBeInTheDocument();
  expect(within(rows[4]).getByText("20,5")).toBeInTheDocument();
});
