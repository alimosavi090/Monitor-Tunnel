"""
Report generation coordinator.
"""
from typing import List
from tunnelbench.benchmark.models import BenchmarkResult
from tunnelbench.reports.exporters import JsonExporter, TxtExporter, MarkdownExporter, HtmlExporter
from tunnelbench.core.logger import log

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.exporters = {
            "json": JsonExporter(output_dir),
            "txt": TxtExporter(output_dir),
            "md": MarkdownExporter(output_dir),
            "html": HtmlExporter(output_dir)
        }

    def generate(self, results: List[BenchmarkResult], formats: List[str] = None) -> dict:
        """
        Generate reports in the specified formats.
        If formats is None, all formats are generated.
        Returns a dict of format -> filepath.
        """
        if formats is None:
            formats = list(self.exporters.keys())
            
        generated_files = {}
        for fmt in formats:
            fmt = fmt.lower()
            if fmt in self.exporters:
                try:
                    filepath = self.exporters[fmt].export(results)
                    generated_files[fmt] = filepath
                    log.debug(f"Generated {fmt.upper()} report: {filepath}")
                except Exception as e:
                    log.error(f"Failed to generate {fmt} report: {e}")
            else:
                log.warning(f"Unknown report format: {fmt}")
                
        return generated_files
