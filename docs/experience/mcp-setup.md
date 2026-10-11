# CareerOS Model Context Protocol (MCP) & Command Engine Integration Guide

CareerOS has evolved from a web application into an **Autonomous Career Operating System**. Every action in the system is a command that can be driven identically from:
1. **The Web UI / Vercel AI SDK chat** (`/api/chat` and `/command`)
2. **The Command Line Interface (CLI)** (`python careeros_cli.py exec <command>`)
3. **The REST Control Channel** (`POST /api/commands` and `POST /api/commands/{name}`)
4. **The Model Context Protocol (MCP) Server** (`python careeros_cli.py mcp` or `python -m engine.mcp.server`)

---

## 1. Registered Core Commands

| Command | Description | Key Arguments |
|---|---|---|
| `gap_analysis` | Evaluates candidate resume against target JD with composite ATS/recruiter rubric | `jd_id`, `cv_text`, `profile_id`, `use_cache` |
| `tailor_resume` | Synthesizes tailored resume and compiles pixel-perfect A4 PDF | `jd_id`, `profile_id`, `fast`, `llm` |
| `evaluate_mandate`| Runs dialectic debate (Prosecutor vs Advocate vs Arbiter) | `jd_id`, `profile_id`, `llm`, `career_mode` |
| `pipeline_status` | Returns pipeline stages, metrics, and active opportunity cards | `stage`, `limit` |
| `ingest_cv` | Parses resume text or file into structured profile and indexes Talent Lake | `cv_text`, `file_path`, `career_mode` |
| `radar_scan` | Autonomous job radar scraping and scoring across job boards | `query`, `location`, `remote`, `limit` |
| `list_commands` | Self-describes all command schemas and descriptors | _(none)_ |

---

## 2. Setting Up CareerOS in Claude Desktop

Add CareerOS to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "careeros": {
      "command": "python",
      "args": [
        "-m",
        "engine.mcp.server"
      ],
      "cwd": "D:\\rouca\\DVM\\workPlace\\CareerOS",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

Once configured, restart Claude Desktop. You will see CareerOS tools appear with hammer icons (`gap_analysis`, `tailor_resume`, `evaluate_mandate`, `pipeline_status`, `ingest_cv`, `radar_scan`).

---

## 3. Setting Up CareerOS in Cursor / Antigravity

In your Cursor or Antigravity workspace settings:
- Add command: `python careeros_cli.py mcp`
- Transport: `stdio`

---

## 4. Driving via CLI

```bash
# List all available commands and schemas
python careeros_cli.py exec list_commands

# Inspect current recruitment pipeline
python careeros_cli.py exec pipeline_status -a '{"limit": 5}'

# Run dialectic debate on JD_01
python careeros_cli.py exec evaluate_mandate -a '{"jd_id": "JD_01", "career_mode": "freelance"}'

# Tailor and compile resume
python careeros_cli.py exec tailor_resume -a '{"jd_id": "JD_01", "fast": true}'
```

---

## 5. Driving via REST Control Channel

```bash
# Query pipeline via HTTP
curl -X POST http://localhost:8000/api/commands/pipeline_status \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Generic command dispatch
curl -X POST http://localhost:8000/api/commands \
  -H "Content-Type: application/json" \
  -d '{
    "command": "gap_analysis",
    "args": {
      "jd_id": "JD_01"
    }
  }'
```
