from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient

from invima_tool.api import app


class ApiTests(unittest.TestCase):
    def test_health_endpoint(self):
        client = TestClient(app)
        response = client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_drug_report_endpoint_shape(self):
        client = TestClient(app)
        response = client.get("/api/drugs/PACLITAXEL/report?only_vigente=true")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["query"], "PACLITAXEL")
        self.assertIn("completion", body)
        self.assertIn("invima", body)
        self.assertIn("source_policy", body)


if __name__ == "__main__":
    unittest.main()

