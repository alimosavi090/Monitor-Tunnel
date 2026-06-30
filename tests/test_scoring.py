import pytest
from tunnelbench.scoring.engine import ScoringEngine
from tunnelbench.benchmark.models import BenchmarkResult, Server

@pytest.fixture
def engine():
    return ScoringEngine()

@pytest.fixture
def server():
    return Server(name="Test", host="1.1.1.1")

def test_perfect_score(engine, server):
    result = BenchmarkResult(
        server=server,
        ping_latency=5.0,     # Perfect
        jitter=2.0,           # Perfect
        packet_loss=0.0,      # Perfect
        download_speed=200.0, # Exceeds 100 max
        upload_speed=100.0,   # Exceeds 50 max
        error=None
    )
    engine.calculate_score(result)
    assert result.score == 100
    assert result.stars == "★★★★★"

def test_terrible_score(engine, server):
    result = BenchmarkResult(
        server=server,
        ping_latency=400.0,   # 0 pts
        jitter=100.0,         # 0 pts
        packet_loss=5.0,      # 0 pts (5 * 7 = 35)
        download_speed=0.0,   # 0 pts
        upload_speed=0.0,     # 0 pts
        error=None
    )
    engine.calculate_score(result)
    assert result.score == 0
    assert result.stars == "☆☆☆☆☆"

def test_error_score(engine, server):
    result = BenchmarkResult(
        server=server,
        packet_loss=100.0,
        error="Timeout"
    )
    engine.calculate_score(result)
    assert result.score == 0
    assert result.success == False
