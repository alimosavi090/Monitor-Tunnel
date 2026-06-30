"""
Report exporters (JSON, HTML, Markdown, TXT).
"""
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any
from tunnelbench.benchmark.models import BenchmarkResult
from tunnelbench.core.exceptions import ReportGenerationError

class BaseExporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def _prepare_data(self, results: List[BenchmarkResult]) -> List[Dict[str, Any]]:
        data = []
        for res in results:
            data.append({
                "server": res.server.name,
                "host": res.server.host,
                "score": res.score if res.score is not None else 0,
                "stars": res.stars,
                "upload_mbps": res.upload_speed,
                "download_mbps": res.download_speed,
                "ping_ms": res.ping_latency,
                "jitter_ms": res.jitter,
                "packet_loss_pct": res.packet_loss,
                "error": res.error
            })
        return data

    def export(self, results: List[BenchmarkResult]) -> str:
        raise NotImplementedError


class JsonExporter(BaseExporter):
    def export(self, results: List[BenchmarkResult]) -> str:
        data = self._prepare_data(results)
        filepath = self.output_dir / f"report_{self.timestamp}.json"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"timestamp": self.timestamp, "results": data}, f, indent=4)
            return str(filepath)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate JSON report: {e}")


class TxtExporter(BaseExporter):
    def export(self, results: List[BenchmarkResult]) -> str:
        data = self._prepare_data(results)
        filepath = self.output_dir / f"report_{self.timestamp}.txt"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("TunnelBench Benchmark Report\n")
                f.write(f"Generated at: {self.timestamp}\n")
                f.write("=================================================\n\n")
                for d in data:
                    f.write(f"Server: {d['server']} ({d['host']})\n")
                    f.write(f"Score: {d['score']} {d['stars']}\n")
                    f.write(f"Download: {d['download_mbps']} Mbps\n")
                    f.write(f"Upload: {d['upload_mbps']} Mbps\n")
                    f.write(f"Ping: {d['ping_ms']} ms (Jitter: {d['jitter_ms']} ms)\n")
                    f.write(f"Packet Loss: {d['packet_loss_pct']}%\n")
                    if d['error']:
                        f.write(f"Error: {d['error']}\n")
                    f.write("-" * 40 + "\n")
            return str(filepath)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate TXT report: {e}")


class MarkdownExporter(BaseExporter):
    def export(self, results: List[BenchmarkResult]) -> str:
        data = self._prepare_data(results)
        filepath = self.output_dir / f"report_{self.timestamp}.md"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# TunnelBench Benchmark Report\n\n")
                f.write(f"**Generated at:** `{self.timestamp}`\n\n")
                
                f.write("| Server | Score | Upload | Download | Ping | Jitter | Loss | Recommendation |\n")
                f.write("|--------|-------|--------|----------|------|--------|------|----------------|\n")
                
                for d in data:
                    err = f"*(Error: {d['error']})*" if d['error'] else ""
                    f.write(f"| {d['server']} | {d['score']} | {d['upload_mbps']} Mbps | {d['download_mbps']} Mbps | "
                            f"{d['ping_ms']} ms | {d['jitter_ms']} ms | {d['packet_loss_pct']}% | {d['stars']} {err}|\n")
            return str(filepath)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate Markdown report: {e}")


class HtmlExporter(BaseExporter):
    def export(self, results: List[BenchmarkResult]) -> str:
        data = self._prepare_data(results)
        filepath = self.output_dir / f"report_{self.timestamp}.html"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>TunnelBench Report</title>\n")
                f.write("<style>\n")
                f.write("body { font-family: Arial, sans-serif; background: #121212; color: #e0e0e0; margin: 40px; }\n")
                f.write("h1 { color: #00e5ff; }\n")
                f.write("table { border-collapse: collapse; width: 100%; margin-top: 20px; }\n")
                f.write("th, td { border: 1px solid #333; padding: 12px; text-align: left; }\n")
                f.write("th { background-color: #1e1e1e; color: #00e5ff; }\n")
                f.write(".stars { color: #ffeb3b; }\n")
                f.write(".error { color: #ff5252; }\n")
                f.write("</style>\n</head>\n<body>\n")
                f.write("<h1>TunnelBench Benchmark Report</h1>\n")
                f.write(f"<p>Generated at: {self.timestamp}</p>\n")
                
                f.write("<table>\n")
                f.write("<tr><th>Server</th><th>Score</th><th>Upload</th><th>Download</th><th>Ping</th><th>Jitter</th><th>Loss</th><th>Recommendation</th></tr>\n")
                for d in data:
                    error_msg = f"<br><span class='error'>{d['error']}</span>" if d['error'] else ""
                    f.write(f"<tr><td>{d['server']}</td><td>{d['score']}</td><td>{d['upload_mbps']} Mbps</td>")
                    f.write(f"<td>{d['download_mbps']} Mbps</td><td>{d['ping_ms']} ms</td><td>{d['jitter_ms']} ms</td>")
                    f.write(f"<td>{d['packet_loss_pct']}%</td><td class='stars'>{d['stars']}{error_msg}</td></tr>\n")
                f.write("</table>\n</body>\n</html>\n")
            return str(filepath)
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate HTML report: {e}")
