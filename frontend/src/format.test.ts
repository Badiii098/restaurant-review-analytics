import { angka, skor100 } from "./format";

test("skor prioritas ditampilkan 0–100 dengan koma desimal", () => {
  expect(skor100(0.8216)).toBe("82,2");
  expect(skor100(0.2054)).toBe("20,5");
});

test("angka memakai pemisah ribuan titik", () => {
  expect(angka(6874)).toBe("6.874");
  expect(angka(0.7123, 3)).toBe("0,712");
});
