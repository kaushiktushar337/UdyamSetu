"""Database integration contract for UdyamSetu's ML/Decision Engine."""
from .decision_engine import result_for_database
from .database_contract import WRITE_TABLE_REQUIRED_COLUMNS


def map_analysis_result(result, analysis_input=None, confidence=None, engine_version=None):
    payload = result_for_database(result, analysis_input)
    if confidence is not None:
        payload["business_analyses"]["confidence"] = round(max(0.0, min(1.0, float(confidence))), 4)
    if engine_version:
        payload["business_analyses"]["engine_version"] = str(engine_version)

    for table, required in WRITE_TABLE_REQUIRED_COLUMNS.items():
        if table not in payload:
            raise ValueError(f"Missing database payload section: {table}")
        missing = required - set(payload[table].keys()) if isinstance(payload[table], dict) else set()
        if missing:
            raise ValueError(f"{table} payload is missing required columns: {sorted(missing)}")
    return payload
