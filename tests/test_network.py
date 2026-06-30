from tunnelbench.network.ping import parse_ping_output

def test_parse_ping_linux_success():
    output = \"\"\"
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=118 time=15.2 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=118 time=14.8 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=118 time=15.5 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 14.800/15.166/15.500/0.288 ms
\"\"\"
    stats = parse_ping_output(output)
    assert stats["packet_loss"] == 0.0
    assert 15.0 < stats["latency"] < 15.3
    # Jitter: |15.2-14.8|=0.4, |14.8-15.5|=0.7 -> (0.4+0.7)/2 = 0.55
    assert stats["jitter"] == 0.55

def test_parse_ping_windows_success():
    output = \"\"\"
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=20ms TTL=118
Reply from 8.8.8.8: bytes=32 time=25ms TTL=118

Ping statistics for 8.8.8.8:
    Packets: Sent = 2, Received = 2, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 20ms, Maximum = 25ms, Average = 22ms
\"\"\"
    stats = parse_ping_output(output)
    assert stats["packet_loss"] == 0.0
    assert stats["latency"] == 22.5
    assert stats["jitter"] == 5.0

def test_parse_ping_100_percent_loss():
    output = \"\"\"
PING 1.2.3.4 (1.2.3.4) 56(84) bytes of data.
--- 1.2.3.4 ping statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 3065ms
\"\"\"
    stats = parse_ping_output(output)
    assert stats["packet_loss"] == 100.0
    assert stats["latency"] == 0.0
