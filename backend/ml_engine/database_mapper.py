"""Database integration contract for UdyamSetu's ML/Decision Engine."""
from .decision_engine import result_for_database
from .database_contract import WRITE_TABLE_REQUIRED_COLUMNS


def map_analysis_result(result, analysis_input=None):
    payload = result_for_database(result, analysis_input)
    for table, required in WRITE_TABLE_REQUIRED_COLUMNS.items():
        if table not in payload:
            raise ValueError(f"Missing database payload section: {table}")
        missing = required - set(payload[table].keys()) if isinstance(payload[table], dict) else set()
        if missing:
            raise ValueError(f"{table} payload is missing required columns: {sorted(missing)}")
    return payload
