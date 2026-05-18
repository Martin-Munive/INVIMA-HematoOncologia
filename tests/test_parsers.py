from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from invima_tool.invima_parser import parse_invima_detail_html, parse_invima_results_html
from invima_tool.manual_parser import parse_manual_text
from invima_tool.pospopuli_parser import parse_pospopuli_results_html
from invima_tool.unirs_parser import filter_unirs, parse_unirs_xlsx

RAW = ROOT / "Datos brutos"


def require_fixture(path: Path) -> Path:
    if not path.exists():
        raise unittest.SkipTest(f"Fixture local no incluido en el repositorio publico: {path.name}")
    return path


class ParserTests(unittest.TestCase):
    def test_invima_results_fixture(self):
        rows = parse_invima_results_html(
            require_fixture(RAW / "Pagina principa al buscar PACLITAXEL_files" / "blanco(4).html")
        )
        self.assertEqual(len(rows), 91)
        self.assertEqual(rows[0].expediente, "20260945")
        self.assertEqual(rows[0].cdgprod, "1813066")
        self.assertIn("PACLITAXEL", rows[0].principio_activo)

    def test_invima_detail_fixture(self):
        detail = parse_invima_detail_html(
            require_fixture(RAW / "Paclitaxel al hacer clic en la primera presentacion_files" / "blanco(4).html")
        )
        self.assertEqual(detail.expediente, "20260945")
        self.assertIn("CÁNCER DE MAMA", detail.indicaciones)
        self.assertEqual(detail.atc, "L01CD01")

    def test_unirs_fixture(self):
        rows = parse_unirs_xlsx(require_fixture(RAW / "UNIRS V24-07-2025.xlsx"))
        hits = filter_unirs(rows, "PACLITAXEL")
        self.assertEqual(len(rows), 917)
        self.assertEqual(len(hits), 8)

    def test_pospopuli_fixture(self):
        rows = parse_pospopuli_results_html(require_fixture(RAW / "POS Pópuli - Busqueda Paclitaxel.html"))
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("UPC" in row.financiacion for row in rows))

    def test_manual_target_parser(self):
        text = """
        PACLITAXEL
        * Antineoplasico taxano.
        EFECTOS ADVERSOS/NO
        * Neuropatia periferica.
        EXTRAVASACION Y CONTROL
        * Exfoliante.
        INDICACION INVIMA
        PACLITAXEL 100 MG
        * Cancer de ovario.
        PEMBROLIZUMAB
        * Inhibidor PD-1.
        """
        rows = parse_manual_text(text, targets=["PACLITAXEL"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].nombre, "PACLITAXEL")
        self.assertIn("Neuropatia", rows[0].efectos_adversos)
        self.assertIn("Exfoliante", rows[0].extravasacion)
        self.assertIn("Cancer de ovario", rows[0].indicacion_manual)

    def test_manual_parser_uses_blank_groups_when_headers_are_missing(self):
        text = """
        ACETATO DE GOSERELINA
        * Analogo de hormona liberadora de gonadotropina.
        * Suprime gonadotropinas.

        * Sofocos.
        * Fatiga.

        CLASIFICACION:
        * No vesicante.
        MANEJO:
        * Retirar la aguja.

        ZOLADEX® 3.6 MG
        * Cancer de mama.
        """
        rows = parse_manual_text(text, targets=["ACETATO DE GOSERELINA"])
        self.assertEqual(len(rows), 1)
        self.assertIn("Analogo", rows[0].mecanismo)
        self.assertIn("Sofocos", rows[0].efectos_adversos)
        self.assertIn("No vesicante", rows[0].extravasacion)
        self.assertIn("Cancer de mama", rows[0].indicacion_manual)


if __name__ == "__main__":
    unittest.main()
