"""
SQLite-based history store.
"""
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from tunnelbench.benchmark.models import BenchmarkResult

class HistoryStore:
    def __init__(self, db_path: str = "history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    server_name TEXT NOT NULL,
                    host TEXT NOT NULL,
                    score INTEGER,
                    stars TEXT,
                    ping_ms REAL,
                    jitter_ms REAL,
                    packet_loss_pct REAL,
                    download_mbps REAL,
                    upload_mbps REAL,
                    error TEXT
                )
            """)
            # Index for faster history lookups by server
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_server_name ON benchmarks(server_name)")
            conn.commit()

    def save_result(self, result: BenchmarkResult):
        """Save a benchmark result to the database."""
        timestamp = datetime.datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO benchmarks (
                    timestamp, server_name, host, score, stars, 
                    ping_ms, jitter_ms, packet_loss_pct, download_mbps, upload_mbps, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, result.server.name, result.server.host,
                result.score if result.score is not None else 0,
                result.stars, result.ping_latency, result.jitter, result.packet_loss,
                result.download_speed, result.upload_speed, result.error
            ))
            conn.commit()

    def get_history(self, server_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve historical benchmarks, optionally filtered by server."""
        query = "SELECT * FROM benchmarks"
        params = []
        if server_name:
            query += " WHERE server_name = ?"
            params.append(server_name)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        results = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                results.append(dict(row))
                
        return results

    def compare_latest(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Compare the most recent benchmark for a server with the one prior to it.
        Returns a dict containing 'latest', 'previous', and 'diff' containing score/speed changes.
        """
        history = self.get_history(server_name, limit=2)
        if len(history) < 2:
            return None # Cannot compare if less than 2 runs

        latest = history[0]
        previous = history[1]
        
        diff = {
            "score": latest["score"] - previous["score"],
            "download_mbps": round(latest["download_mbps"] - previous["download_mbps"], 2),
            "upload_mbps": round(latest["upload_mbps"] - previous["upload_mbps"], 2),
            "ping_ms": round(latest["ping_ms"] - previous["ping_ms"], 2)
        }
        
        return {
            "server": server_name,
            "latest": latest,
            "previous": previous,
            "diff": diff
        }
