from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import urlopen


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def _fetch_json(url: str, timeout: int) -> dict:
    with urlopen(url, timeout=timeout) as response:
        payload = response.read().decode("utf-8", errors="replace")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object from {url}")
    return data


def _fetch_status(url: str, timeout: int) -> int:
    with urlopen(url, timeout=timeout) as response:
        response.read()
        return response.status


def check_api_health(api_base: str, timeout: int) -> CheckResult:
    try:
        data = _fetch_json(f"{api_base}/api/health", timeout)
    except (OSError, URLError, ValueError, json.JSONDecodeError) as exc:
        return CheckResult("api_health", False, str(exc))
    return CheckResult("api_health", data.get("status") == "ok", f"status={data.get('status')!r}")


def check_report_contract(api_base: str, drug: str, timeout: int) -> CheckResult:
    try:
        data = _fetch_json(f"{api_base}/api/drugs/{drug}/report?only_vigente=true", timeout)
    except (OSError, URLError, ValueError, json.JSONDecodeError) as exc:
        return CheckResult("report_contract", False, str(exc))

    invima = data.get("invima")
    completion = data.get("completion")
    required = {
        "completion": isinstance(completion, dict),
        "invima": isinstance(invima, dict),
        "invima.details": isinstance(invima, dict) and isinstance(invima.get("details"), list),
        "invima.open_cum": isinstance(invima, dict) and isinstance(invima.get("open_cum"), list),
        "invima.open_cum_count": isinstance(invima, dict) and isinstance(invima.get("open_cum_count"), int),
        "source_policy": isinstance(data.get("source_policy"), dict),
    }
    missing = [name for name, ok in required.items() if not ok]
    if missing:
        return CheckResult("report_contract", False, "missing_or_invalid=" + ",".join(missing))
    return CheckResult(
        "report_contract",
        True,
        f"details={invima.get('details_count', 0)} open_cum={invima.get('open_cum_count', 0)}",
    )


def check_frontend(frontend_url: str, timeout: int) -> CheckResult:
    try:
        status = _fetch_status(frontend_url, timeout)
    except (OSError, URLError) as exc:
        return CheckResult("frontend_http", False, str(exc))
    return CheckResult("frontend_http", 200 <= status < 300, f"status={status}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Local smoke check for INVIMA API and frontend.")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000")
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--drug", default="PACLITAXEL")
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    results = [
        check_api_health(args.api_base, args.timeout),
        check_report_contract(args.api_base, args.drug, args.timeout),
        check_frontend(args.frontend_url, args.timeout),
    ]

    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"{status} {result.name}: {result.detail}")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
