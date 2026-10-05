"""Shared rules for source provenance and usable commercial observations."""

from datetime import date, timedelta, datetime, timezone
import math
from urllib.parse import urlparse


def valid_url(value):
    try:
        parsed = urlparse(value or "")
        return parsed.scheme in {"https", "http"} and bool(parsed.hostname) and not parsed.username
    except (ValueError, TypeError):
        return False


def source_type_for(url, label="", declared=None):
    """Document classification does not establish that its content was verified."""
    host = (urlparse(url or "").hostname or "").lower()
    if any(host == d or host.endswith("." + d) for d in ("fravega.com", "supertoolsbd.com", "mercadolibre.com.ar", "puntogardenia.com.ar", "gramabi.com.ar")):
        return "comercio"
    official = ("bosch-professional.com", "bosch-diy.com", "einhell.com.ar", "lusqtoff.com.ar", "gammaherramientas.com.ar", "makita.com.ar", "kaercher.com", "stihl.com.ar", "dewalt.com", "dewalt.com.ar", "dewalt.global", "dewalt.fr", "stanleytools.global", "stanleytools.com.ar", "esab.com", "honda.com.ar", "btatools.com.ar", "gadnic.com.ar", "logus.com.ar")
    if not any(host == d or host.endswith('.' + d) for d in official):
        return "documento_en_tercero" if '.pdf' in url.lower() else "referencia_externa"
    text = label.lower()
    if "despiece" in text:
        return "despiece_oficial"
    if "catálogo" in text or "catalogo" in text:
        return "catalogo_oficial"
    if ".pdf" in url.lower() and ("manual" in text or declared == 'manual_oficial'):
        return "manual_oficial"
    return "ficha_fabricante"


def usable_spec(spec):
    value = spec.normalized_value
    return (spec.status in {"declarado", "medido", "calculado"}
            and isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and valid_url(spec.source_url)
            and getattr(spec, 'documentary_status', '') not in {'sin_respaldo', 'identidad_no_coincidente', 'referencia_comercial'})


def latest_verified_offer(tool, today=None):
    """Only recent observations with retained evidence can be presented as current."""
    today = today or datetime.now(timezone.utc).date()
    eligible = []
    for offer in tool.offers:
        try:
            observed = date.fromisoformat(offer.observation_date)
            price = offer.observed_price_ars
            if (offer.verification_status == "verificado" and offer.evidence_reference
                    and valid_url(offer.url) and isinstance(price, (int, float))
                    and not isinstance(price, bool) and math.isfinite(price) and price > 0
                    and today - timedelta(days=7) <= observed <= today):
                eligible.append(offer)
        except (ValueError, TypeError):
            continue
    return max(eligible, key=lambda o: (o.observation_date, o.url)) if eligible else None


# A model page is only offered to search engines when it carries enough
# located, manufacturer-backed values to be useful on its own. Pages below the
# threshold stay reachable for readers (noindex, follow) and leave the sitemap.
MIN_INDEXABLE_BACKED_SPECS = 3


def backed_specs(tool):
    return [s for s in tool.specifications if getattr(s, 'documentary_status', '') == 'concordancia_textual']


def tool_is_indexable(tool):
    return len(backed_specs(tool)) >= MIN_INDEXABLE_BACKED_SPECS
