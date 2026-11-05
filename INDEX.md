# INDEX — what's in this repository

A guided map of AICHAT_LAB. Start with [`README.md`](README.md) for the overview and
[`CLAUDE_SKILL.md`](CLAUDE_SKILL.md) for how the lab is continued.

## Top level
| Path | What it is |
|------|------------|
| `README.md` | The showcase: what the lab is, the agents, the two core ideas, quickstart, and a note for AI readers. |
| `CLAUDE_SKILL.md` | The reusable AI skill that maintains the lab (reproduced in full) + the principles behind it. |
| `INDEX.md` | This file. |
| `LEARNING_LOG.md` | Running project notes and the learning journey (built by a non-developer). |
| `WINDOWS_HANDOFF.md` | Notes for extending the lab onto a second machine (Windows / RTX) over the LAN. |
| `checkpoints/` | Frozen, working versions for rollback (VER_1, WORKING_V1/V2/V3...). Restore: copy a checkpoint's `lab/` over `lab/`. |
| `lab/` | The live project. |

## lab/ — the live project
| Path | What it is |
|------|------------|
| `lab/DESIGN.md` | How it works, step by step (engine vs config, transport, control channel, memory, graph). |
| `lab/README.md` | How to run each agent and the console. |
| `lab/VERSION` | Stamp of the running version (shown by `caps` and the console header). |
| `lab/lab.py` | The console: monitor, follow, reset, judge, caps, params, model, control, configure, errors, graph, evals. |
| `lab/IDEAS_FROM_AGENTS.md` | **The ideas the agents themselves discovered** — buildable lab upgrades, Batch 1 (trust/consensus) + Batch 2 (graph quality & retrieval). |
| `lab/IDEAS_GRAPH_MEMORY.md` | Earlier design notes on graph-as-memory. |

### lab/agents/ — one folder per agent (`agent.py` + `config.json`)
| Agent | Role |
|-------|------|
| `alice/` | chat peer, drives the conversation (reads the shared graph each turn). |
| `bob/` | chat peer, answers (reads the shared graph each turn). |
| `carlos/` | director + judge; extracts the knowledge graph from the chat. |
| `aradia/` | reflective ideator; reads the graph and proposes new lab concepts. |

### lab/modules/ — opt-in capabilities (toggled by `config.modules`)
| Module | What it adds |
|--------|--------------|
| `memory_graph.py` | Parse `subject \| relation \| object` triples, dedup into `graph.json`, render `graph.md`. |
| `ideator.py` | Aradia's brain: build a prompt from the graph, parse generated concepts. |
| `hello.py` | Demo module that proves the loader. |

### lab/logs/ — the lab's running record (git-ignored except snapshots)
| File | What it is |
|------|------------|
| `events.jsonl` | The transcript (what each agent said). |
| `trace.jsonl` | How each turn was produced (prompt size, timing, decisions). |
| `errors.jsonl` | Every exception with traceback (the log catcher). |
| `control.json` | The control channel (run / pause / stop / inject). |
| `graph.json` + `graph.md` | The shared knowledge graph (data + rendered diagram). |
| `mem_<name>.txt` | Each agent's simple memory notes. |
| `aradia_ideas.md` | Concepts Aradia generated from the graph. |

### lab/ tests (offline, model stubbed)
`test_agent.py` · `test_graph.py` · `test_lab.py` · `test_ideator.py` — run before any live run.
