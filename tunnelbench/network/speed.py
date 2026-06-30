"""
Speed test module (Download/Upload).
"""
import time
import requests
from tunnelbench.core.exceptions import NetworkError

# A common reliable endpoint for speed tests (Cloudflare)
SPEEDTEST_URL = "https://speed.cloudflare.com/__down?bytes={size}"
UPLOAD_URL = "https://speed.cloudflare.com/__up"

def measure_download_speed(proxies: dict = None, size_mb: int = 10) -> float:
    """
    Measure download speed in Mbps.
    
    Args:
        proxies: Dictionary of proxies (e.g., {"http": "...", "https": "..."})
        size_mb: Size of file to download in MB.
        
    Returns:
        float: Download speed in Mbps.
    """
    bytes_to_download = size_mb * 1024 * 1024
    url = SPEEDTEST_URL.format(size=bytes_to_download)
    
    start_time = time.time()
    try:
        response = requests.get(url, proxies=proxies, stream=True, timeout=10)
        response.raise_for_status()
        
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                downloaded += len(chunk)
                
        duration = time.time() - start_time
        if duration == 0:
            return 0.0
            
        # Convert bytes/sec to Mbps (Megabits per second)
        speed_bps = (downloaded * 8) / duration
        speed_mbps = speed_bps / 1_000_000
        return round(speed_mbps, 2)
        
    except Exception as e:
        raise NetworkError(f"Download speed test failed: {e}")


def measure_upload_speed(proxies: dict = None, size_mb: int = 5) -> float:
    """
    Measure upload speed in Mbps.
    
    Args:
        proxies: Dictionary of proxies (e.g., {"http": "...", "https": "..."})
        size_mb: Size of dummy payload to upload in MB.
        
    Returns:
        float: Upload speed in Mbps.
    """
    bytes_to_upload = size_mb * 1024 * 1024
    dummy_data = b"0" * bytes_to_upload
    
    start_time = time.time()
    try:
        response = requests.post(UPLOAD_URL, data=dummy_data, proxies=proxies, timeout=15)
        response.raise_for_status()
        
        duration = time.time() - start_time
        if duration == 0:
            return 0.0
            
        speed_bps = (bytes_to_upload * 8) / duration
        speed_mbps = speed_bps / 1_000_000
        return round(speed_mbps, 2)
        
    except Exception as e:
        raise NetworkError(f"Upload speed test failed: {e}")
