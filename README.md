# FortiAnalyzer MCP NG

`fortianalyzer-mcp-ng` is a maintained fork of [`rstierli/fortianalyzer-mcp`](https://github.com/rstierli/fortianalyzer-mcp). It exposes the FortiAnalyzer JSON-RPC API as an MCP server so Claude Desktop, Claude Code, LM Studio, Open WebUI, and other MCP-compatible clients can query logs, run reports, inspect FortiView data, manage incidents, and automate common FortiAnalyzer workflows.

This project is not affiliated with, endorsed by, or supported by Fortinet. FortiAnalyzer is a trademark of Fortinet, Inc.

## Why this fork exists

This fork keeps the original scope, but fixes a few release and runtime issues that matter in practice:

- publishable package name and CLI entrypoint: `fortianalyzer-mcp-ng`
- dynamic tool mode repaired so report tools can actually be discovered and executed
- HTTP `/health` now reflects the real FAZ connection state and returns `503` when disconnected
- safer report filename handling for exported files
- more consistent total counters in log and PCAP responses
- logging setup now accepts `LOG_FORMAT=json` cleanly
- packaging fixed so editable installs and wheel builds work under the renamed distribution

## Feature overview

- traffic, threat, event, and related log queries
- FortiView analytics and top-N summaries
- report discovery, execution, polling, and export
- PCAP search and download workflows
- alert, event, incident, and IOC operations
- device and ADOM management helpers
- stdio mode for desktop MCP clients and HTTP mode for container or gateway deployments

## Requirements

- Python 3.12+
- a reachable FortiAnalyzer instance with JSON-RPC API access
- an API token or username/password with the permissions you need
- HTTPS connectivity from the host running this server to FortiAnalyzer

## Quick start

```bash
git clone https://github.com/<your-user>/fortianalyzer-mcp-ng.git
cd fortianalyzer-mcp-ng

uv venv
source .venv/bin/activate
uv sync

cp .env.example .env
```

Minimal `.env`:

```env
FORTIANALYZER_HOST=faz.example.local
FORTIANALYZER_API_TOKEN=replace-me
FORTIANALYZER_VERIFY_SSL=false
DEFAULT_ADOM=root
FAZ_TOOL_MODE=full
LOG_LEVEL=INFO
```

Run locally:

```bash
fortianalyzer-mcp-ng
```

The legacy alias `fortianalyzer-mcp` is still installed for compatibility, but `fortianalyzer-mcp-ng` is the preferred command for this fork.

## Installation

### Option 1: `uv` (recommended)

```bash
git clone https://github.com/<your-user>/fortianalyzer-mcp-ng.git
cd fortianalyzer-mcp-ng

uv venv
source .venv/bin/activate
uv sync
```

### Option 2: `pip`

```bash
git clone https://github.com/<your-user>/fortianalyzer-mcp-ng.git
cd fortianalyzer-mcp-ng

python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Option 3: Docker / Compose

This repository ships a local `Dockerfile` and `docker-compose.yml`. The image is built locally from the checked-out source, so no prebuilt registry image is required.

```bash
cp .env.example .env
docker compose up --build -d
```

The included compose setup exposes port `8001`, mounts `./logs` and `./output`, and enables report/PCAP file writes inside `/app/output`.

## Configuration

Create your local config from the example file:

```bash
cp .env.example .env
```

Important settings:

| Variable | Required | Purpose |
| --- | --- | --- |
| `FORTIANALYZER_HOST` | yes | Hostname or IP of the FortiAnalyzer appliance |
| `FORTIANALYZER_API_TOKEN` | recommended | Preferred authentication method |
| `FORTIANALYZER_USERNAME` / `FORTIANALYZER_PASSWORD` | optional | Alternative to token auth |
| `FORTIANALYZER_VERIFY_SSL` | no | Set `false` for self-signed lab environments |
| `DEFAULT_ADOM` | no | Default ADOM used when a tool omits one |
| `FAZ_TOOL_MODE` | no | `full` or `dynamic` |
| `MCP_SERVER_MODE` | no | `stdio`, `http`, or `auto` |
| `MCP_AUTH_TOKEN` | no | Bearer token for HTTP deployments |
| `MCP_ALLOWED_HOSTS` | no | JSON array of allowed reverse-proxy host headers |
| `FAZ_ALLOWED_OUTPUT_DIRS` | no | Comma-separated allowlist for report and PCAP output paths |

### Tool modes

| Mode | What loads | When to use it |
| --- | --- | --- |
| `full` | all registered tools | default and simplest choice |
| `dynamic` | discovery surface plus on-demand execution | useful when client context budget matters |

Dynamic mode is fixed in this fork and is safe to use again. If you want the least surprising behavior, keep `FAZ_TOOL_MODE=full`.

### File output security

This project is secure by default for file writes:

- query and read tools work without any output directory setting
- file-writing tools such as report export or PCAP download require `FAZ_ALLOWED_OUTPUT_DIRS`
- writes outside the allowlist are rejected

For Docker, the bundled compose file mounts `./output` and sets `FAZ_ALLOWED_OUTPUT_DIRS=/app/output`.

## Running the server

### Stdio mode

Use stdio mode when the server is launched directly by an MCP client:

```bash
fortianalyzer-mcp-ng
```

or:

```bash
python -m fortianalyzer_mcp
```

### HTTP mode

Use HTTP mode for Docker, remote gateway, or reverse proxy deployments:

```bash
MCP_SERVER_MODE=http fortianalyzer-mcp-ng
```

Health check:

```bash
curl http://localhost:8001/health
```

Typical healthy response:

```json
{
  "status": "healthy",
  "service": "fortianalyzer-mcp-ng",
  "fortianalyzer_connected": true,
  "tool_mode": "full"
}
```

If the FortiAnalyzer connection is unavailable, `/health` returns HTTP `503` with `status: "degraded"`.

## Claude Desktop

Example Claude Desktop config entry:

```json
{
  "mcpServers": {
    "fortianalyzer-ng": {
      "command": "/absolute/path/to/fortianalyzer-mcp-ng/.venv/bin/fortianalyzer-mcp-ng",
      "env": {
        "FORTIANALYZER_HOST": "faz.example.local",
        "FORTIANALYZER_API_TOKEN": "replace-me",
        "FORTIANALYZER_VERIFY_SSL": "false",
        "DEFAULT_ADOM": "root",
        "FAZ_TOOL_MODE": "full",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Claude Code

Example `~/.claude/mcp_servers.json` entry:

```json
{
  "mcpServers": {
    "fortianalyzer-ng": {
      "command": "/absolute/path/to/fortianalyzer-mcp-ng/.venv/bin/fortianalyzer-mcp-ng",
      "env": {
        "FORTIANALYZER_HOST": "faz.example.local",
        "FORTIANALYZER_API_TOKEN": "replace-me",
        "FORTIANALYZER_VERIFY_SSL": "false",
        "DEFAULT_ADOM": "root",
        "FAZ_TOOL_MODE": "full",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Security notes

- store API tokens in `.env` or secret management, never in source control
- enable SSL verification in production whenever possible
- use least-privilege FAZ accounts
- protect `.env` files with restrictive permissions such as `chmod 600 .env`
- set `MCP_AUTH_TOKEN` when exposing the HTTP endpoint beyond localhost

## Testing

Development install:

```bash
pip install -e '.[dev]'
```

Run the non-integration suite:

```bash
FORTIANALYZER_HOST=test-faz.example.com \
FORTIANALYZER_API_TOKEN=dummy \
DEFAULT_ADOM=root \
pytest -m "not integration"
```

Current fork status:

- `341 passed`
- `56 deselected`

## What changed compared with upstream

- dynamic execution map repaired for report operations
- health reporting made truthful for both MCP and HTTP surfaces
- report export path handling tightened for safer file writes
- packaging adjusted for the renamed `-ng` distribution
- logging setup made more robust in local and CI environments

## Upstream, license, and support

- upstream project: [`rstierli/fortianalyzer-mcp`](https://github.com/rstierli/fortianalyzer-mcp)
- this fork started from upstream commit `48c5bba`
- license: [MIT](LICENSE)

Small, reviewable fixes are intentional so cherry-picking changes upstream remains easy.
