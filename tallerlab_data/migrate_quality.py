"""Conservative, repeatable metadata migration; never reload technical values."""

from contextlib import closing
from tallerlab_data import storage
from tallerlab_data.quality import source_type_for


def migrate_quality_metadata():
    storage.init_db()
    with closing(storage.get_connection()) as connection:
        rows = connection.execute("SELECT id, source_name, source_url, source_type, document_page FROM tool_specs").fetchall()
        for row in rows:
            kind = source_type_for(row["source_url"], row["source_name"])
            page = None if row["document_page"] == "pág. 1" else row["document_page"]
            connection.execute("UPDATE tool_specs SET source_type=?, document_page=? WHERE id=?", (kind, page, row["id"]))
        # The initial catalog has no retained capture evidence for its prices.
        connection.execute("UPDATE tool_offers SET verification_status='archivado_sin_evidencia' WHERE evidence_reference=''")
        connection.execute("""UPDATE tool_specs SET condition='LpA según ficha Einhell Argentina',
                           notes='Ficha Einhell Argentina declara 70 dB(A) LpA; no extrapolar a otro punto de medición.'
                           WHERE tool_slug='einhell-te-ac-270-50-silent' AND spec_key='nivel_sonoro'
                           AND condition='LpA oficial según ficha Einhell Argentina; folletos previos reportaban 65 dB(A) a 7 m'""")
        connection.commit()


if __name__ == "__main__":
    migrate_quality_metadata()
