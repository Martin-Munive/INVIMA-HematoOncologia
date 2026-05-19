from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from invima_tool.cli import DB_PATH
from invima_tool.reporting import _query_terms, build_drug_report, build_drug_suggestions


class ReportingTests(unittest.TestCase):
    def test_query_terms_strip_common_salt_prefixes(self):
        self.assertEqual(_query_terms("ACETATO DE GOSERELINA"), ["ACETATO DE GOSERELINA", "GOSERELINA"])
        self.assertEqual(_query_terms("ACIDO ZOLEDRONICO"), ["ACIDO ZOLEDRONICO", "ZOLEDRONICO"])

    def test_report_shape_includes_invima_fields(self):
        report = build_drug_report(DB_PATH, "PACLITAXEL", only_vigente=True)
        self.assertIn("details_count", report["invima"])
        self.assertIn("details", report["invima"])
        self.assertIn("registration_source", report["source_policy"])

    def test_drug_suggestions_shape(self):
        if not DB_PATH.exists():
            raise unittest.SkipTest("Base SQLite local no incluida en el repositorio publico")
        suggestions = build_drug_suggestions(DB_PATH, "PACL", limit=5)
        self.assertTrue(any(item["name"] == "PACLITAXEL" for item in suggestions))
        self.assertIn("sources", suggestions[0])

    def test_paclitaxel_report_shape_when_local_db_exists(self):
        if not DB_PATH.exists():
            raise unittest.SkipTest("Base SQLite local no incluida en el repositorio publico")

        report = build_drug_report(DB_PATH, "PACLITAXEL", only_vigente=True)

        self.assertEqual(report["query"], "PACLITAXEL")
        self.assertTrue(report["only_vigente"])
        self.assertIn("completion", report)
        self.assertIn("invima", report)
        self.assertIn("unirs", report)
        self.assertIn("pospopuli", report)
        self.assertIn("clinical_safety", report)
        self.assertIn("source_policy", report)


if __name__ == "__main__":
    unittest.main()
