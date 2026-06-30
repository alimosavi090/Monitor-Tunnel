"""
Score and Star calculation engine for benchmark results.
"""
from tunnelbench.benchmark.models import BenchmarkResult

class ScoringEngine:
    def __init__(self, max_download_mbps: float = 1000.0, max_upload_mbps: float = 1000.0):
        # We benchmark against an ideal 1Gbps connection, but cap speeds to this for scoring
        self.max_download_mbps = max_download_mbps
        self.max_upload_mbps = max_upload_mbps

    def calculate_score(self, result: BenchmarkResult) -> None:
        """
        Calculate score (0-100) and assign stars to the given BenchmarkResult.
        Modifies the result object in-place.
        """
        if not result.success:
            result.score = 0
            result.stars = "☆☆☆☆☆"
            return

        score = 0.0

        # 1. Packet Loss (Max 35 points)
        # 0% loss = 35 pts, 5% or more = 0 pts
        loss_pts = max(0, 35 - (result.packet_loss * 7))
        score += loss_pts

        # 2. Ping Latency (Max 25 points)
        # 0ms = 25 pts, 300ms or more = 0 pts
        ping_pts = max(0, 25 - (result.ping_latency * (25 / 300)))
        score += ping_pts

        # 3. Jitter (Max 10 points)
        # 0ms = 10 pts, 50ms or more = 0 pts
        jitter_pts = max(0, 10 - (result.jitter * (10 / 50)))
        score += jitter_pts

        # 4. Download Speed (Max 15 points)
        # Assuming 100 Mbps is a great baseline for full points in typical VPN use
        download_pts = min(15, (result.download_speed / 100.0) * 15)
        score += download_pts

        # 5. Upload Speed (Max 15 points)
        # Assuming 50 Mbps is great for VPN upload
        upload_pts = min(15, (result.upload_speed / 50.0) * 15)
        score += upload_pts

        final_score = int(round(score))
        result.score = max(0, min(100, final_score))
        result.stars = self._calculate_stars(result.score)

    def _calculate_stars(self, score: int) -> str:
        if score >= 90:
            return "★★★★★"
        elif score >= 75:
            return "★★★★☆"
        elif score >= 60:
            return "★★★☆☆"
        elif score >= 40:
            return "★★☆☆☆"
        elif score > 0:
            return "★☆☆☆☆"
        else:
            return "☆☆☆☆☆"
