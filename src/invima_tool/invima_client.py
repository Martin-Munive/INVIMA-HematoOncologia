from __future__ import annotations

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .invima_parser import parse_invima_detail_html
from .models import InvimaDetail

DETAIL_ENDPOINT = (
    "https://consultaregistro.invima.gov.co/Consultas/consultas/"
    "consproductocum.jsp"
)


def fetch_invima_detail_by_expediente(
    expediente: str,
    cdgprod: str,
    timeout: int = 30,
) -> InvimaDetail:
    body = urlencode(
        {
            "nroexpediente": expediente,
            "grupo": "2",
            "cdgprod": cdgprod,
            "buscarPor": "principio",
        }
    ).encode("ascii")
    request = Request(
        DETAIL_ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "INVIMA-local-research-tool/0.1",
        },
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
    html = raw.decode("utf-8", errors="replace")
    detail = parse_invima_detail_html(html, is_html=True)
    if not detail.expediente or not detail.indicaciones:
        raise ValueError(
            "INVIMA detail endpoint responded, but did not return a complete product "
            "detail for the supplied expediente/cdgprod."
        )
    if detail.expediente != expediente:
        raise ValueError(
            "INVIMA detail endpoint returned a different expediente "
            f"({detail.expediente}) than requested ({expediente})."
        )
    object.__setattr__(detail, "cdgprod", cdgprod)
    return detail
