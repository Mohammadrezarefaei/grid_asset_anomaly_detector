import sqlite3
import pandas as pd

class AssetAnomalyDB:
    def __init__(self, db_name="grid_asset_health.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Initialize database schema for transformer telemetry and anomaly tracking."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                load_mw REAL,
                top_oil_temp_c REAL,
                vibration_mms REAL,
                is_anomaly INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_telemetry_batch(self, df_telemetry):
        """Save telemetry records and anomaly detection flags to the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for _, row in df_telemetry.iterrows():
            cursor.execute('''
                INSERT INTO telemetry_logs (timestamp, load_mw, top_oil_temp_c, vibration_mms, is_anomaly)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(row['timestamp']),
                float(row['load_mw']),
                float(row['top_oil_temp_c']),
                float(row['vibration_mms']),
                int(row['is_anomaly'])
            ))
            
        conn.commit()
        conn.close()
        return len(df_telemetry)
