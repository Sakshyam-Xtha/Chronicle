import json 
import sqlite3
from chronicle.storage.models import Findings

class FindingsRepo:
    def __init__(self,conn:sqlite3.Connection) -> None:
        self.conn = conn
        
    def save(self, finding:Findings) -> bool:
        cursor = self.conn.execute(
            """
            INSERT INTO 
            findings(
                analyzer,
                severity,
                title,
                message,
                observation_id,
                data
            ) VALUES (?,?,?,?,?,?)
            """,
            (
                finding.analyzer,
                finding.severity,  
                finding.title,
                finding.message,
                finding.observation_id,
                json.dumps(finding.data), 
            ),
        )
        
        return cursor.rowcount == 1
    
    def list_all(self) -> list[Findings]:
        findings = []
        
        rows = self.conn.execute(
        """
        SELECT * FROM findings ORDER BY observation_id;
        """
        ).fetchall()
        
        for row in rows:
            findings.append(Findings(
                analyzer=row["analyzer"],
                severity=row["severity"],
                title=row["title"],
                message=row["message"],
                observation_id=row["observation_id"],
                data=json.loads(row["data"]),
            ))
            
        return findings