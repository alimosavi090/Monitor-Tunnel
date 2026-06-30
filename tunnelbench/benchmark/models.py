"""
Data models for servers and benchmark results.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Server:
    name: str
    host: str
    proxy_url: Optional[str] = None  # E.g., 'socks5://user:pass@host:port' or 'http://...'
    speedtest_url: Optional[str] = None # E.g., 'http://1.2.3.4:8080'
    
    def get_proxies(self) -> Optional[dict]:
        """Return the proxies dictionary for requests if a proxy_url is set."""
        if not self.proxy_url:
            return None
        return {
            "http": self.proxy_url,
            "https": self.proxy_url
        }

@dataclass
class BenchmarkResult:
    server: Server
    ping_latency: float = 0.0
    jitter: float = 0.0
    packet_loss: float = 100.0
    download_speed: float = 0.0
    upload_speed: float = 0.0
    error: Optional[str] = None
    score: Optional[int] = None
    stars: str = "☆☆☆☆☆"
    
    @property
    def success(self) -> bool:
        return self.error is None and self.packet_loss < 100.0
