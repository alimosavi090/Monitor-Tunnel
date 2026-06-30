"""
Benchmark runner.
"""
from tunnelbench.benchmark.models import Server, BenchmarkResult
from tunnelbench.network.ping import measure_ping
from tunnelbench.network.speed import measure_download_speed, measure_upload_speed
from tunnelbench.core.logger import log

class BenchmarkRunner:
    def __init__(self, ping_count: int = 10, speedtest_size_mb: int = 10):
        self.ping_count = ping_count
        self.speedtest_size_mb = speedtest_size_mb

    def run(self, server: Server) -> BenchmarkResult:
        """
        Run a full benchmark suite against a single server.
        """
        log.debug(f"Starting benchmark for server {server.name} ({server.host})")
        result = BenchmarkResult(server=server)
        
        try:
            # 1. Ping test (Latency, Jitter, Packet Loss)
            log.debug(f"Pinging {server.host}...")
            ping_stats = measure_ping(server.host, count=self.ping_count)
            result.ping_latency = ping_stats["latency"]
            result.jitter = ping_stats["jitter"]
            result.packet_loss = ping_stats["packet_loss"]
            
            # If 100% packet loss, no need to run speed test
            if result.packet_loss == 100.0:
                result.error = "Host unreachable (100% packet loss)"
                return result
                
            proxies = server.get_proxies()
            
            # 2. Download Speed test
            log.debug(f"Measuring download speed for {server.name}...")
            result.download_speed = measure_download_speed(
                proxies=proxies, 
                size_mb=self.speedtest_size_mb
            )
            
            # 3. Upload Speed test
            log.debug(f"Measuring upload speed for {server.name}...")
            result.upload_speed = measure_upload_speed(
                proxies=proxies, 
                size_mb=max(1, self.speedtest_size_mb // 2)
            )
            
        except Exception as e:
            log.error(f"Error benchmarking {server.name}: {e}")
            result.error = str(e)
            
        return result
