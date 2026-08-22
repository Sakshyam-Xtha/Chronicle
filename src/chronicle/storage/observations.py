import json
import sqlite3
from chronicle.scanners.models import Observation

class ObservationRepo:
    def __init__(self, connection:sqlite3.Connection) -> None:
        self.conn = connection
        
    def save(self,observation:Observation)->bool:
        cursor = self.conn.execute(
            """
            INSERT OR IGNORE INTO observations(
                source,
                type,
                external_id,
                timestamp,
                data
            ) VALUES (?,?,?,?,?)
            """,
            (
                observation.source,
                observation.type,
                observation.external_id,
                observation.timestamp.isoformat(),
                json.dumps(observation.data),
            ),
        )
        
        self.conn.commit()
        
        return cursor.rowcount == 1