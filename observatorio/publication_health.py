"""Comprueba la publicación; una fuente aislada fallida no detiene las demás."""
from datetime import datetime, timezone


def publication_warning(report, expected_finished_at, now=None):
    run = report['run']
    if run['finished_at'] != expected_finished_at:
        raise ValueError('Pages todavía sirve una captura anterior')
    finished = datetime.fromisoformat(run['finished_at'])
    if finished.tzinfo is None:
        raise ValueError('La captura no tiene zona horaria')
    age = ((now or datetime.now(timezone.utc)) - finished).total_seconds()
    if age < 0 or age > 48 * 3600:
        raise ValueError('La captura publicada está vencida o tiene fecha futura')
    if run['status'] not in ('ok', 'degraded'):
        raise ValueError('La captura no terminó')
    if run['captured'] + run.get('already_captured', 0) <= 0:
        raise ValueError('No se pudo verificar ningún producto')
    if report['unverified'] or report['stale'] or run['status'] == 'degraded':
        return (f"Publicado: {report['unverified']} productos sin verificación y "
                f"{report['stale']} vencidos. Se ocultan y se reintentan en la próxima captura.")
    return None
