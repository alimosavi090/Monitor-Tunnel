"""
Ping and jitter measurement tools.
"""
import subprocess
import platform
import statistics
import re
from tunnelbench.core.exceptions import NetworkError

def measure_ping(host: str, count: int = 10, timeout: int = 2) -> dict:
    """
    Measure ping, packet loss, and jitter to a host.
    
    Args:
        host: Hostname or IP to ping.
        count: Number of ping packets to send.
        timeout: Timeout per packet in seconds.
        
    Returns:
        dict: Contains 'latency' (ms), 'jitter' (ms), and 'packet_loss' (percentage).
    """
    system = platform.system().lower()
    
    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        # Linux / MacOS
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]

    try:
        # We allow a bit of extra time for the subprocess to complete
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=count * timeout + 5)
    except subprocess.TimeoutExpired:
        return {"latency": 0.0, "jitter": 0.0, "packet_loss": 100.0}
    except Exception as e:
        raise NetworkError(f"Failed to execute ping command: {e}")

    return parse_ping_output(result.stdout)

def parse_ping_output(output: str) -> dict:
    """Parse ping CLI output to extract stats."""
    # Extract times
    times = []
    # matches time=15.2 ms or time<1ms
    time_matches = re.finditer(r"time[=<]\s*([\d.]+)\s*ms", output, re.IGNORECASE)
    for match in time_matches:
        try:
            times.append(float(match.group(1)))
        except ValueError:
            pass

    # Extract packet loss
    packet_loss = 100.0
    loss_match = re.search(r"(\d+(?:\.\d+)?)%\s*packet\s*loss", output, re.IGNORECASE)
    if not loss_match:
        # Try Windows format: (0% loss)
        loss_match = re.search(r"\((\d+)%\s*loss\)", output, re.IGNORECASE)
        
    if loss_match:
        packet_loss = float(loss_match.group(1))
    elif len(times) > 0:
        # Fallback if regex fails but we have times, we can estimate
        packet_loss = 0.0 # Not perfectly accurate if count isn't known, but safe

    if not times:
        return {"latency": 0.0, "jitter": 0.0, "packet_loss": 100.0}

    latency = sum(times) / len(times)
    
    # Calculate jitter (average of absolute differences between consecutive pings)
    jitter = 0.0
    if len(times) > 1:
        diffs = [abs(times[i] - times[i-1]) for i in range(1, len(times))]
        jitter = sum(diffs) / len(diffs)

    return {
        "latency": round(latency, 2),
        "jitter": round(jitter, 2),
        "packet_loss": round(packet_loss, 2)
    }
