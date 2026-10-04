import os
import pandas as pd
import pytest
from database.anomaly_db_logger import AssetAnomalyDB

@pytest.fixture
def temp_anomaly_db(tmp_path):
    db_path = tmp_path / "test_anomaly.db"
    return AssetAnomalyDB(db_name=str(db_path))

def test_anomaly_database_logging(temp_anomaly_db):
    df_mock = pd.DataFrame({
        'timestamp': ['2026-10-04 10:00:00', '2026-10-04 11:00:00'],
        'load_mw': [45.0, 52.3],
        'top_oil_temp_c': [55.0, 85.5],
        'vibration_mms': [1.1, 4.8],
        'is_anomaly': [0, 1]
    })
    
    count = temp_anomaly_db.save_telemetry_batch(df_mock)
    assert count == 2
    
    import sqlite3
    conn = sqlite3.connect(temp_anomaly_db.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM telemetry_logs WHERE is_anomaly = 1")
    anomaly_count = cursor.fetchone()[0]
    conn.close()
    
    assert anomaly_count == 1
