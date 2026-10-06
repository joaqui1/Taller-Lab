"""Una única regla de elegibilidad para todas las salidas públicas."""
PUBLIC_OBSERVATION_SQL = """
    o.validation_status='valido' AND o.is_published=1 AND o.is_synthetic=0
    AND off.enabled=1 AND src.status='habilitada'
    AND src.capture_allowed=1 AND src.redistribution_allowed=1
    AND src.terms_verified_date IS NOT NULL
"""
