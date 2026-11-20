import { render, screen } from "@testing-library/react";
import { BelumTersedia } from "./BelumTersedia";

test("menampilkan perintah pembuat bukti", () => {
  render(<BelumTersedia langkah="python -m rra.cli run" />);
  expect(screen.getByText("python -m rra.cli run")).toBeInTheDocument();
  expect(screen.getByText(/belum tersedia/i)).toBeInTheDocument();
});
