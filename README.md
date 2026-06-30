# TunnelBench

<p align="center">
  <b>A powerful, professional CLI application for benchmarking VPN servers for heavy tunnel usage.</b><br>
  <i>Identify routing issues, poor upload speeds, and high packet loss before your users do.</i>
</p>

---

## ⚡ Features

- **Colorful CLI**: Built with `Rich` for beautiful tables, animated progress bars, and colored warnings.
- **Multi-Server Mode**: Accept a list of servers and benchmark them sequentially.
- **Smart Scoring Engine**: Calculates an out-of-100 score and assigns a 5-star rating based on Download, Upload, Ping, Jitter, and Packet Loss.
- **Multi-Format Reports**: Automatically generates and saves reports in JSON, HTML, TXT, and Markdown.
- **History & Comparison**: Saves every benchmark to a local SQLite database and allows you to compare current performance against previous runs.
- **YAML Configuration**: Easily manage hundreds of servers using a clean `config.yaml` file.

---

## 🚀 Installation

TunnelBench requires Python 3.9 or higher.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alimosavi090/Monitor-Tunnel.git
   cd Monitor-Tunnel
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

---

## ⚙️ Configuration

TunnelBench uses a `config.yaml` file to define the servers you want to benchmark. Place this file in the directory where you run the tool.

```yaml
# config.yaml
servers:
  - name: NL-1
    host: 104.18.2.1
    proxy_url: socks5://user:pass@104.18.2.1:1080
  - name: DE-2
    host: 104.18.3.1
  - name: FI-1
    host: 104.18.4.1
```

*(Note: `proxy_url` is optional. If omitted, the tool will just perform standard network tests against the `host`)*

---

## 💻 Usage & Examples

TunnelBench is driven by an intuitive CLI.

### 1. Benchmark Servers
Run a full benchmark suite. You can pass server names directly, or leave it blank to test all servers in your `config.yaml`.

```bash
# Benchmark all servers in config
tunnelbench benchmark

# Benchmark specific servers
tunnelbench benchmark NL-1 DE-2

# Enable debug logging for troubleshooting
tunnelbench benchmark --debug
```

### 2. Compare with Previous Runs
Analyze if a server's performance has degraded or improved since its last benchmark.

```bash
tunnelbench compare NL-1
```

### 3. Generate Reports
Run benchmarks and automatically save the results to the `reports/` directory in JSON, HTML, Markdown, and TXT formats.

```bash
tunnelbench report
```

### 4. View History
Look up the historical performance of your network from the local SQLite database.

```bash
# View the last 10 global benchmarks
tunnelbench history

# View history for a specific server
tunnelbench history NL-1 --limit 5
```

---

## 📸 Screenshots

*(Imagine beautifully rendered terminal outputs here!)*

**Ranking Example Table:**
```text
┏━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Server   ┃ Score ┃ Upload   ┃ Download ┃ Jitter ┃ Loss ┃ Recommendation ┃
┡━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━┩
│ NL-1     │ 98    │ 94.0 Mbps│ 200.0 Mbps│ 0.5 ms │ 0.0% │ ★★★★★          │
│ DE-2     │ 95    │ 87.0 Mbps│ 180.0 Mbps│ 0.8 ms │ 0.0% │ ★★★★★          │
│ FI-1     │ 89    │ 64.0 Mbps│ 110.0 Mbps│ 1.4 ms │ 0.0% │ ★★★★☆          │
│ UK-1     │ 63    │ 22.0 Mbps│ 40.0 Mbps │ 7.0 ms │ 1.0% │ ★★☆☆☆          │
└──────────┴───────┴──────────┴──────────┴────────┴──────┴────────────────┘
```

**Comparison Panel:**
```text
╭──────────────── Comparison: NL-1 ─────────────────╮
│ Score: 98 (Change: +3)                            │
│ Download: 200.0 Mbps (Change: +15.50)             │
│ Upload: 94.0 Mbps (Change: -2.00)                 │
│ Ping: 12.5 ms (Change: -0.50)                     │
╰───────────────────────────────────────────────────╯
```

---

## ❓ FAQ

**Q: Why does a server get 0 stars?**  
A: A score of 0 typically indicates catastrophic failure, such as 100% packet loss (the host is unreachable) or a severe proxy authentication error. 

**Q: Where are the history logs stored?**  
A: History is securely stored in a local SQLite database named `history.db` in the directory you execute the command from.

**Q: How is the score calculated?**  
A: The Scoring Engine starts with 100 points and mathematically deducts points based on packet loss severity, high ping, high jitter, and sub-optimal bandwidth targets.

---
*Built with ❤️ for Network Engineers.*
