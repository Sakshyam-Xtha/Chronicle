import sqlite3
from datetime import datetime, timezone

class ScanStateRepo:
    def __init__(self,conn:sqlite3.Connection) -> None:
        self.conn = conn
        
    def get(self,key:str,scanner:str) -> str | None:
        row = self.conn.execute(
            """
            SELECT VALUE FROM scan_state WHERE key=? AND scanner=?;
            """,
            (key,scanner),
        ).fetchone()
        
        if row is None:
            return None
        
        return row["value"] 
    
    def set(self,key:str,scanner:str,value:str) -> None:
        self.conn.execute(
            """
            INSERT INTO scan_state(
                scanner,
                key,
                value,
                updated_at
            )
            VALUES (?,?,?,?)
            
            ON CONFLICT(scanner,key)
            DO UPDATE SET 
            value = excluded.value,
            updated_at = excluded.updated_at
            """,
            (
                scanner,
                key,
                value,
                datetime.now(timezone.utc).isoformat(),
            )
        )
        
        self.conn.commit()