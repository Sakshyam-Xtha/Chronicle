import json
import sqlite3
from chronicle.storage.models import Observation
from datetime import datetime

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
        
        return cursor.rowcount == 1
    
    def list_all(self,id:int | None = None) -> list[Observation]:
        observations = []
        if id:
            row = self.conn.execute(
                """
                SELECT
                    id,
                    source,
                    type,
                    external_id,
                    timestamp,
                    data
                FROM observations 
                WHERE id = ?;
                """,
                (id,),
            ).fetchone()
            
            if row is None:
                return []
            
            observations.append(
                Observation(
                    source=row["source"],
                    type=row["type"],
                    external_id=row["external_id"],
                    timestamp=datetime.fromisoformat(
                        row["timestamp"]
                    ),
                    data=json.loads(row["data"]),
                )
            )
        else:
            rows = self.conn.execute(
                """
                SELECT
                    id,
                    source,
                    type,
                    external_id,
                    timestamp,
                    data
                FROM observations
                ORDER BY id
                """
            ).fetchall()
            
            for row in rows:
                observations.append(
                    Observation(
                        id=row["id"],
                        source=row["source"],
                        type=row["type"],
                        external_id=row["external_id"],
                        timestamp=datetime.fromisoformat(
                            row["timestamp"]
                        ),
                        data=json.loads(row["data"]),
                    )
                )
                
        return observations