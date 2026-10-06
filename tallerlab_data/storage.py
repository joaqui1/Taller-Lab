"""Capa de almacenamiento y persistencia para TallerLab Data."""

import json
import re
import sqlite3
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from tallerlab_data.models import (
    CommercialOffer,
    ContradictionRecord,
    KitOption,
    RegionalVariant,
    Specification,
    TechnicalTool,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(tempfile.gettempdir()) / "tallerlab-data-catalog.db" if os.environ.get('VERCEL') else DATA_DIR / "tallerlab_data.db"
_bootstrap_lock = threading.RLock()
_bootstrapping = False


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    global _bootstrapping
    target = Path(db_path or DB_PATH)
    snapshot = DATA_DIR / 'catalog_snapshot.json'
    with _bootstrap_lock:
        if not target.exists() and snapshot.exists() and not _bootstrapping:
            _bootstrapping = True
            staging = target.with_name(target.name + '.bootstrap-' + str(os.getpid()))
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                init_db(staging)
                payload = json.loads(snapshot.read_text(encoding='utf-8'))
                for item in payload['tools']:
                    save_tool(tool_from_dict(item), staging)
                for candidate in payload.get('candidates', []):
                    add_candidate(candidate['candidate_code'], candidate['brand'], candidate['model_name'], candidate['category'], json.loads(candidate['raw_payload_json']), candidate['rejection_or_pending_reason'], staging, status=candidate['status'])
                for c in payload.get('corrections', []):
                    add_correction(c['correction_date'], c['tool_slug'], c['field_affected'], c['old_value'], c['new_value'], c['reason'], c['source'], staging)
                staging.replace(target)
            finally:
                staging.unlink(missing_ok=True)
                _bootstrapping = False
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS tools (
        slug TEXT PRIMARY KEY,
        brand TEXT NOT NULL,
        commercial_name TEXT NOT NULL,
        mpn TEXT NOT NULL,
        category TEXT NOT NULL,
        summary TEXT NOT NULL,
        primary_use TEXT NOT NULL,
        power_source TEXT NOT NULL,
        limits_and_warnings_json TEXT NOT NULL,
        primary_sources_json TEXT NOT NULL,
        last_reviewed TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'aceptado'
    );

    CREATE TABLE IF NOT EXISTS tool_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_slug TEXT NOT NULL,
        spec_key TEXT NOT NULL,
        name TEXT NOT NULL,
        raw_value TEXT NOT NULL,
        raw_unit TEXT NOT NULL,
        normalized_value REAL,
        normalized_unit TEXT NOT NULL,
        condition TEXT NOT NULL,
        applicable_variant TEXT NOT NULL,
        applicable_market TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source_name TEXT NOT NULL,
        source_url TEXT NOT NULL,
        document_page TEXT,
        consultation_date TEXT NOT NULL,
        status TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (tool_slug) REFERENCES tools(slug) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tool_variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_slug TEXT NOT NULL,
        code TEXT NOT NULL,
        market TEXT NOT NULL,
        voltage_frequency TEXT NOT NULL,
        plug_type TEXT,
        notes TEXT,
        FOREIGN KEY (tool_slug) REFERENCES tools(slug) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tool_kits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_slug TEXT NOT NULL,
        kit_code TEXT NOT NULL,
        description TEXT NOT NULL,
        battery_included TEXT NOT NULL,
        charger_included TEXT NOT NULL,
        accessories_json TEXT NOT NULL,
        FOREIGN KEY (tool_slug) REFERENCES tools(slug) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tool_offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_slug TEXT NOT NULL,
        seller TEXT NOT NULL,
        platform TEXT NOT NULL,
        url TEXT NOT NULL,
        observed_price_ars REAL,
        observation_date TEXT NOT NULL,
        item_condition TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        FOREIGN KEY (tool_slug) REFERENCES tools(slug) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tool_contradictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_slug TEXT NOT NULL,
        spec_key TEXT NOT NULL,
        field_name TEXT NOT NULL,
        source_a_name TEXT NOT NULL,
        source_a_value TEXT NOT NULL,
        source_a_url TEXT NOT NULL,
        source_b_name TEXT NOT NULL,
        source_b_value TEXT NOT NULL,
        source_b_url TEXT NOT NULL,
        editorial_note TEXT NOT NULL,
        FOREIGN KEY (tool_slug) REFERENCES tools(slug) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_code TEXT NOT NULL,
        brand TEXT NOT NULL,
        model_name TEXT NOT NULL,
        category TEXT NOT NULL,
        raw_payload_json TEXT NOT NULL,
        rejection_or_pending_reason TEXT,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pendiente'
    );

    CREATE TABLE IF NOT EXISTS corrections_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correction_date TEXT NOT NULL,
        tool_slug TEXT NOT NULL,
        field_affected TEXT NOT NULL,
        old_value TEXT NOT NULL,
        new_value TEXT NOT NULL,
        reason TEXT NOT NULL,
        source TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_tool_specs_slug ON tool_specs(tool_slug);
    CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
    """)
    # Additive migration; existing observations remain pending without evidence.
    spec_columns = {row[1] for row in cur.execute('PRAGMA table_info(tool_specs)')}
    for name in ('documentary_status', 'evidence_reference', 'evidence_excerpt', 'condition_status'):
        if name not in spec_columns:
            cur.execute(f"ALTER TABLE tool_specs ADD COLUMN {name} TEXT NOT NULL DEFAULT ''")
    columns = {row[1] for row in cur.execute("PRAGMA table_info(tool_offers)")}
    for name, default in [("evidence_reference", ""), ("observed_availability", "desconocida"),
                          ("variant_code", ""), ("kit_code", ""), ("valid_until", "")]:
        if name not in columns:
            cur.execute(f"ALTER TABLE tool_offers ADD COLUMN {name} TEXT NOT NULL DEFAULT '{default}'")
    conn.commit()
    conn.close()


def save_tool(tool: TechnicalTool, db_path: Optional[Path] = None) -> None:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tools (slug, brand, commercial_name, mpn, category, summary, primary_use, power_source, limits_and_warnings_json, primary_sources_json, last_reviewed, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(slug) DO UPDATE SET
        brand=excluded.brand,
        commercial_name=excluded.commercial_name,
        mpn=excluded.mpn,
        category=excluded.category,
        summary=excluded.summary,
        primary_use=excluded.primary_use,
        power_source=excluded.power_source,
        limits_and_warnings_json=excluded.limits_and_warnings_json,
        primary_sources_json=excluded.primary_sources_json,
        last_reviewed=excluded.last_reviewed,
        status=excluded.status
    """, (
        tool.slug,
        tool.brand,
        tool.commercial_name,
        tool.mpn,
        tool.category,
        tool.summary,
        tool.primary_use,
        tool.power_source,
        json.dumps(tool.limits_and_warnings, ensure_ascii=False),
        json.dumps(tool.primary_sources, ensure_ascii=False),
        tool.last_reviewed,
        tool.status,
    ))

    # Reemplazar relaciones técnicas del modelo
    cur.execute("DELETE FROM tool_specs WHERE tool_slug = ?", (tool.slug,))
    cur.execute("DELETE FROM tool_variants WHERE tool_slug = ?", (tool.slug,))
    cur.execute("DELETE FROM tool_kits WHERE tool_slug = ?", (tool.slug,))
    cur.execute("DELETE FROM tool_contradictions WHERE tool_slug = ?", (tool.slug,))

    for spec in tool.specs.values():
        cur.execute("""
        INSERT INTO tool_specs (tool_slug, spec_key, name, raw_value, raw_unit, normalized_value, normalized_unit, condition, applicable_variant, applicable_market, source_type, source_name, source_url, document_page, consultation_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tool.slug, spec.spec_key, spec.name, spec.raw_value, spec.raw_unit,
            spec.normalized_value, spec.normalized_unit, spec.condition,
            spec.applicable_variant, spec.applicable_market, spec.source_type,
            spec.source_name, spec.source_url, spec.document_page,
            spec.consultation_date, spec.status, spec.notes
        ))
        cur.execute('UPDATE tool_specs SET documentary_status=?, evidence_reference=?, evidence_excerpt=?, condition_status=? WHERE id=?', (spec.documentary_status, spec.evidence_reference, spec.evidence_excerpt, spec.condition_status, cur.lastrowid))

    for var in tool.variants:
        cur.execute("""
        INSERT INTO tool_variants (tool_slug, code, market, voltage_frequency, plug_type, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (tool.slug, var.code, var.market, var.voltage_frequency, var.plug_type, var.notes))

    for kit in tool.kits:
        cur.execute("""
        INSERT INTO tool_kits (tool_slug, kit_code, description, battery_included, charger_included, accessories_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (tool.slug, kit.kit_code, kit.description, kit.battery_included, kit.charger_included, json.dumps(kit.accessories, ensure_ascii=False)))

    # Preservar historial de ofertas comerciales con actualización de estado
    cur.execute("SELECT id, url, observation_date FROM tool_offers WHERE tool_slug = ?", (tool.slug,))
    existing_offers = {(r[1], r[2]): r[0] for r in cur.fetchall()}
    for off in tool.commercial_offers:
        key = (off.url, off.observation_date)
        if key in existing_offers:
            cur.execute("""
            UPDATE tool_offers
            SET seller = ?, platform = ?, observed_price_ars = ?, item_condition = ?, verification_status = ?
            WHERE id = ?
            """, (off.seller, off.platform, off.observed_price_ars, off.item_condition, off.verification_status, existing_offers[key]))
        else:
            cur.execute("""
            INSERT INTO tool_offers (tool_slug, seller, platform, url, observed_price_ars, observation_date, item_condition, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tool.slug, off.seller, off.platform, off.url, off.observed_price_ars, off.observation_date, off.item_condition, off.verification_status))

    for off in tool.commercial_offers:
        cur.execute("""UPDATE tool_offers SET evidence_reference=?, observed_availability=?,
                    variant_code=?, kit_code=?, valid_until=? WHERE tool_slug=? AND url=? AND observation_date=?""",
                    (off.evidence_reference, off.observed_availability, off.variant_code, off.kit_code,
                     off.valid_until, tool.slug, off.url, off.observation_date))

    for con in tool.contradictions:
        cur.execute("""
        INSERT INTO tool_contradictions (tool_slug, spec_key, field_name, source_a_name, source_a_value, source_a_url, source_b_name, source_b_value, source_b_url, editorial_note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tool.slug, con.spec_key, con.field_name, con.source_a_name, con.source_a_value, con.source_a_url, con.source_b_name, con.source_b_value, con.source_b_url, con.editorial_note))

    conn.commit()
    conn.close()


def _row_to_tool(row: sqlite3.Row, cur: sqlite3.Cursor) -> TechnicalTool:
    slug = row["slug"]

    # Specs
    cur.execute("SELECT * FROM tool_specs WHERE tool_slug = ?", (slug,))
    specs = {}
    for r in cur.fetchall():
        specs[r["spec_key"]] = Specification(
            spec_key=r["spec_key"],
            name=r["name"],
            raw_value=r["raw_value"],
            raw_unit=r["raw_unit"],
            normalized_value=r["normalized_value"],
            normalized_unit=r["normalized_unit"],
            condition=r["condition"],
            applicable_variant=r["applicable_variant"],
            applicable_market=r["applicable_market"],
            source_type=r["source_type"],
            source_name=r["source_name"],
            source_url=r["source_url"],
            document_page=r["document_page"],
            consultation_date=r["consultation_date"],
            status=r["status"],
            notes=r["notes"],
            documentary_status=r['documentary_status'] if 'documentary_status' in r.keys() else '',
            evidence_reference=r['evidence_reference'] if 'evidence_reference' in r.keys() else '',
            evidence_excerpt=r['evidence_excerpt'] if 'evidence_excerpt' in r.keys() else '',
            condition_status=r['condition_status'] if 'condition_status' in r.keys() else '',
        )

    # Variants
    cur.execute("SELECT * FROM tool_variants WHERE tool_slug = ?", (slug,))
    variants = [
        RegionalVariant(
            code=r["code"],
            market=r["market"],
            voltage_frequency=r["voltage_frequency"],
            plug_type=r["plug_type"],
            notes=r["notes"],
        ) for r in cur.fetchall()
    ]

    # Kits
    cur.execute("SELECT * FROM tool_kits WHERE tool_slug = ?", (slug,))
    kits = [
        KitOption(
            kit_code=r["kit_code"],
            description=r["description"],
            battery_included=r["battery_included"],
            charger_included=r["charger_included"],
            accessories=json.loads(r["accessories_json"]),
        ) for r in cur.fetchall()
    ]

    # Offers
    cur.execute("SELECT * FROM tool_offers WHERE tool_slug = ?", (slug,))
    offers = [
        CommercialOffer(
            seller=r["seller"],
            platform=r["platform"],
            url=r["url"],
            observed_price_ars=r["observed_price_ars"],
            observation_date=r["observation_date"],
            item_condition=r["item_condition"],
            verification_status=r["verification_status"],
            evidence_reference=r["evidence_reference"] if "evidence_reference" in r.keys() else "",
            observed_availability=r["observed_availability"] if "observed_availability" in r.keys() else "desconocida",
            variant_code=r["variant_code"] if "variant_code" in r.keys() else "",
            kit_code=r["kit_code"] if "kit_code" in r.keys() else "",
            valid_until=r["valid_until"] if "valid_until" in r.keys() else "",
        ) for r in cur.fetchall()
    ]

    # Contradictions
    cur.execute("SELECT * FROM tool_contradictions WHERE tool_slug = ?", (slug,))
    contradictions = [
        ContradictionRecord(
            spec_key=r["spec_key"],
            field_name=r["field_name"],
            source_a_name=r["source_a_name"],
            source_a_value=r["source_a_value"],
            source_a_url=r["source_a_url"],
            source_b_name=r["source_b_name"],
            source_b_value=r["source_b_value"],
            source_b_url=r["source_b_url"],
            editorial_note=r["editorial_note"],
        ) for r in cur.fetchall()
    ]

    return TechnicalTool(
        slug=row["slug"],
        brand=row["brand"],
        commercial_name=row["commercial_name"],
        mpn=row["mpn"],
        category=row["category"],
        summary=row["summary"],
        primary_use=row["primary_use"],
        power_source=row["power_source"],
        specs=specs,
        variants=variants,
        kits=kits,
        commercial_offers=offers,
        contradictions=contradictions,
        limits_and_warnings=json.loads(row["limits_and_warnings_json"]),
        primary_sources=json.loads(row["primary_sources_json"]),
        last_reviewed=row["last_reviewed"],
        status=row["status"],
    )


TOOL_SLUGS_ALIAS_MAP: Dict[str, str] = {
    "lusqtoff-lc2550b": "lusqtoff-lc2550b-8",
    "einhell-te-ac-270-50": "einhell-te-ac-270-50-silent",
    "lusqtoff-lc2024": "lusqtoff-lc2024b",
    "karcher-k4": "karcher-k4-power-control",
    "karcher-k5": "karcher-k5-base",
    "honda-eg6500cx": "honda-eg6500cxs",
}


def get_tool(slug: str, db_path: Optional[Path] = None) -> Optional[TechnicalTool]:
    """Recupera un modelo por su slug exacto o alias registrado. Devuelve None ante cadenas vacías o sin coincidencia."""
    if not slug or not slug.strip():
        return None
    clean_slug = slug.strip()
    target_slug = TOOL_SLUGS_ALIAS_MAP.get(clean_slug, clean_slug)

    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tools WHERE slug = ?", (target_slug,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    tool = _row_to_tool(row, cur)
    conn.close()
    return tool


def list_tools(category: Optional[str] = None, status: str = "aceptado", db_path: Optional[Path] = None) -> List[TechnicalTool]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    if category:
        cur.execute("SELECT * FROM tools WHERE category = ? AND status = ? ORDER BY brand, commercial_name", (category, status))
    else:
        cur.execute("SELECT * FROM tools WHERE status = ? ORDER BY category, brand, commercial_name", (status,))
    rows = cur.fetchall()
    tools = [_row_to_tool(r, cur) for r in rows]
    conn.close()
    return tools


def add_candidate(candidate_code: str, brand: str, model_name: str, category: str, raw_payload: Dict[str, Any], reason: str, db_path: Optional[Path] = None, status: str = 'pendiente') -> None:
    """Inserta o actualiza un candidato en cuarentena de forma idempotente."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM candidates WHERE candidate_code = ?", (candidate_code,))
    existing = cur.fetchone()
    if existing:
        cur.execute("""
        UPDATE candidates SET brand = ?, model_name = ?, category = ?, raw_payload_json = ?, rejection_or_pending_reason = ?, status = ?
        WHERE candidate_code = ?
        """, (brand, model_name, category, json.dumps(raw_payload, ensure_ascii=False), reason, status, candidate_code))
    else:
        cur.execute("""
        INSERT INTO candidates (candidate_code, brand, model_name, category, raw_payload_json, rejection_or_pending_reason, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
        """, (candidate_code, brand, model_name, category, json.dumps(raw_payload, ensure_ascii=False), reason, status))
    conn.commit()
    conn.close()


class ItemRecord(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        if name == "exclusion_reason":
            return self.get("rejection_or_pending_reason", "Falta de manual")
        if name == "review_date":
            return self.get("created_at", "2026-10-01")
        if name == "date":
            return self.get("correction_date", "2026-10-01")
        if name == "spec_name":
            return self.get("field_affected", "")
        if name == "previous_value":
            return self.get("old_value", "")
        if name == "corrected_value":
            return self.get("new_value", "")
        if name == "source_citation":
            return self.get("source", "")
        return ""


_TEST_NAME = re.compile(r'^\s*test[\s_-]*\d*\s*$', re.IGNORECASE)
_TEST_BRANDS = {'modelo incompleto', 'test', 'prueba'}


def is_test_candidate(candidate: Any) -> bool:
    """Registros creados por suites de verificación: nunca deben publicarse."""
    brand = str(candidate.get('brand', '') or '').strip().lower()
    model = str(candidate.get('model_name', '') or '')
    code = str(candidate.get('candidate_code', '') or '')
    return (brand in _TEST_BRANDS or bool(_TEST_NAME.match(model))
            or code.upper().startswith('TEST-'))


def list_candidates(db_path: Optional[Path] = None, include_test: bool = False) -> List[Any]:
    """Candidatos registrados. Por defecto excluye los registros de prueba
    para que nunca lleguen al snapshot ni a la metodología pública."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidates ORDER BY id ASC")
    rows = [ItemRecord(dict(r)) for r in cur.fetchall()]
    conn.close()
    if not include_test:
        rows = [r for r in rows if not is_test_candidate(r)]
    return rows


def add_correction(correction_date: str, tool_slug: str, field_affected: str, old_value: str, new_value: str, reason: str, source: str, db_path: Optional[Path] = None) -> None:
    """Inserta una corrección de forma idempotente sin duplicar registros al reiniciar la semilla."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM corrections_log WHERE tool_slug = ? AND field_affected = ? AND correction_date = ?", (tool_slug, field_affected, correction_date))
    existing = cur.fetchone()
    if not existing:
        cur.execute("""
        INSERT INTO corrections_log (correction_date, tool_slug, field_affected, old_value, new_value, reason, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (correction_date, tool_slug, field_affected, old_value, new_value, reason, source))
        conn.commit()
    conn.close()


def list_corrections(db_path: Optional[Path] = None) -> List[Any]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM corrections_log ORDER BY correction_date DESC, id DESC")
    rows = [ItemRecord(dict(r)) for r in cur.fetchall()]
    conn.close()
    return rows


get_tool_by_slug = get_tool
get_tools_by_category = list_tools
get_all_tools = list_tools


def tool_from_dict(item):
    data = dict(item)
    data['specs'] = {key: Specification(**value) for key, value in data['specs'].items()}
    for key, model in [('variants', RegionalVariant), ('kits', KitOption), ('commercial_offers', CommercialOffer), ('contradictions', ContradictionRecord)]:
        data[key] = [model(**value) for value in data.get(key, [])]
    return TechnicalTool(**data)


def get_all_categories(db_path: Optional[Path] = None) -> List[str]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM tools WHERE status = 'aceptado' ORDER BY category")
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return cats or ["compresores", "hidrolavadoras", "generadores", "soldadoras", "sierras", "taladros", "amoladoras"]


