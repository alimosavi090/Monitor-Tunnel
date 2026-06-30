"""
CLI entry point using Typer and Rich.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from typing import List, Optional
from tunnelbench.core.config import Config
from tunnelbench.core.logger import setup_logger, log
from tunnelbench.benchmark.models import Server
from tunnelbench.benchmark.runner import BenchmarkRunner
from tunnelbench.scoring.engine import ScoringEngine
from tunnelbench.reports.generator import ReportGenerator
from tunnelbench.history.store import HistoryStore

app = typer.Typer(help="TunnelBench - Professional VPN Benchmarking CLI", no_args_is_help=True)
console = Console()

# Global instances
config = Config()
history_store = HistoryStore()
scoring_engine = ScoringEngine()

def load_servers(server_names: List[str] = None) -> List[Server]:
    """Helper to parse servers from args or config."""
    try:
        config.load()
    except Exception as e:
        # If config doesn't exist, it's fine unless we have no server names
        if not server_names:
            console.print(f"[red]Error:[/red] No servers provided and failed to load config: {e}")
            raise typer.Exit(code=1)

    servers = []
    config_servers = config.get("servers", [])
    
    if server_names:
        for name in server_names:
            # Check if this name is in config
            match = next((s for s in config_servers if s.get("name") == name), None)
            if match:
                servers.append(Server(name=match["name"], host=match["host"], proxy_url=match.get("proxy_url")))
            else:
                # Treat as a host directly if not in config
                servers.append(Server(name=name, host=name))
    else:
        for s in config_servers:
            servers.append(Server(name=s["name"], host=s["host"], proxy_url=s.get("proxy_url")))

    if not servers:
        console.print("[red]No servers configured to benchmark![/red]")
        raise typer.Exit(1)
        
    return servers

def run_benchmarks(servers: List[Server], runner: BenchmarkRunner) -> List[any]:
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        overall_task = progress.add_task("[cyan]Benchmarking Servers...", total=len(servers))
        
        for server in servers:
            progress.update(overall_task, description=f"[cyan]Benchmarking {server.name}...")
            
            result = runner.run(server)
            scoring_engine.calculate_score(result)
            history_store.save_result(result)
            results.append(result)
            
            progress.advance(overall_task)
            
    return results

@app.command()
def benchmark(
    servers: Optional[List[str]] = typer.Argument(None, help="List of server names or IPs to benchmark."),
    ping_count: int = typer.Option(10, help="Number of ping packets per server."),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging.")
):
    """
    Run benchmarks on servers and generate a ranking table.
    """
    setup_logger(debug=debug)
    server_list = load_servers(servers)
    runner = BenchmarkRunner(ping_count=ping_count)
    
    results = run_benchmarks(server_list, runner)
    
    # Sort results by score (descending)
    results.sort(key=lambda r: r.score if r.score is not None else -1, reverse=True)
    
    # Generate Table
    table = Table(title="TunnelBench Ranking", show_header=True, header_style="bold magenta")
    table.add_column("Server", style="cyan")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Upload", justify="right")
    table.add_column("Download", justify="right")
    table.add_column("Jitter", justify="right")
    table.add_column("Loss", justify="right")
    table.add_column("Recommendation", justify="center")
    
    for r in results:
        err = f"[red]{r.error}[/red]" if r.error else ""
        stars_colored = f"[yellow]{r.stars}[/yellow]"
        table.add_row(
            r.server.name,
            str(r.score) if r.success else "ERR",
            f"{r.upload_speed} Mbps",
            f"{r.download_speed} Mbps",
            f"{r.jitter} ms",
            f"{r.packet_loss}%",
            f"{stars_colored} {err}"
        )
        
    console.print(table)

@app.command()
def compare(server: str = typer.Argument(..., help="Name of the server to compare.")):
    """
    Compare a server's latest benchmark against its previous benchmark.
    """
    data = history_store.compare_latest(server)
    if not data:
        console.print(f"[yellow]Not enough history to compare server: {server}. Run at least 2 benchmarks.[/yellow]")
        return
        
    diff = data["diff"]
    score_color = "green" if diff["score"] >= 0 else "red"
    dl_color = "green" if diff["download_mbps"] >= 0 else "red"
    ul_color = "green" if diff["upload_mbps"] >= 0 else "red"
    ping_color = "green" if diff["ping_ms"] <= 0 else "red"
    
    content = f"""
    [bold cyan]Score:[/bold cyan] {data['latest']['score']} (Change: [{score_color}]{diff['score']:+d}[/{score_color}])
    [bold cyan]Download:[/bold cyan] {data['latest']['download_mbps']} Mbps (Change: [{dl_color}]{diff['download_mbps']:+.2f}[/{dl_color}])
    [bold cyan]Upload:[/bold cyan] {data['latest']['upload_mbps']} Mbps (Change: [{ul_color}]{diff['upload_mbps']:+.2f}[/{ul_color}])
    [bold cyan]Ping:[/bold cyan] {data['latest']['ping_ms']} ms (Change: [{ping_color}]{diff['ping_ms']:+.2f}[/{ping_color}])
    """
    
    console.print(Panel(content, title=f"Comparison: {server}", expand=False))

@app.command()
def report(
    servers: Optional[List[str]] = typer.Argument(None, help="Servers to report on."),
    output_dir: str = typer.Option("reports", help="Directory to save reports.")
):
    """
    Run benchmarks and export reports to JSON, HTML, TXT, and Markdown.
    """
    server_list = load_servers(servers)
    runner = BenchmarkRunner()
    results = run_benchmarks(server_list, runner)
    
    generator = ReportGenerator(output_dir=output_dir)
    files = generator.generate(results)
    
    console.print("\n[bold green]Reports generated successfully:[/bold green]")
    for fmt, path in files.items():
        console.print(f"- [magenta]{fmt.upper()}[/magenta]: {path}")

@app.command()
def history(server: Optional[str] = typer.Argument(None, help="Filter by server name"), limit: int = 10):
    """
    View historical benchmark results.
    """
    records = history_store.get_history(server_name=server, limit=limit)
    if not records:
        console.print("[yellow]No history found.[/yellow]")
        return
        
    table = Table(title=f"Benchmark History (Last {limit})", header_style="bold blue")
    table.add_column("Date")
    table.add_column("Server")
    table.add_column("Score")
    table.add_column("DL/UL (Mbps)")
    table.add_column("Ping (ms)")
    
    for r in records:
        dt = r["timestamp"].replace("T", " ")[:16]
        table.add_row(
            dt,
            r["server_name"],
            str(r["score"]),
            f"{r['download_mbps']}/{r['upload_mbps']}",
            str(r["ping_ms"])
        )
        
    console.print(table)

if __name__ == "__main__":
    app()
