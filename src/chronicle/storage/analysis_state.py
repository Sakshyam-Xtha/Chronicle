import sqlite3
from datetime import datetime, timezone

class AnalysisStateRepo:
    def __init__(self,conn:sqlite3.Connection) -> None:
        self.conn = conn
        
    def get(self,key:str,analyzer:str) -> str | None:
        row = self.conn.execute(
            """
            SELECT value FROM analysis_state WHERE key=? AND analyzer=?;
            """,
            (key,analyzer),
        ).fetchone()
        
        if row is None:
            return None
        
        return row["value"] 
    
    def set(self,key:str,analyzer:str,value:str) -> None:
        self.conn.execute(
            """
            INSERT INTO analysis_state(
                analyzer,
                key,
                value,
                updated_at
            )
            VALUES (?,?,?,?)
            
            ON CONFLICT(analyzer,key)
            DO UPDATE SET 
            value = excluded.value,
            updated_at = excluded.updated_at
            """,
            (
                analyzer,
                key,
                value,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        