# AICHATBASIC — local multi-agent AI lab

Three local Ollama agents on a Mac: **Alice** and **Bob** chat, **Carlos** directs & judges.
Config-driven, menu-run, fully offline (no cloud API keys). Built step by step as a hands-on
way to learn agentic AI.

- `lab/` — the live project (agents, `lab.py` console, modules, tests, docs)
- `lab/DESIGN.md` — how it works, step by step
- `lab/README.md` — how to run it
- `checkpoints/` — frozen, working versions for rollback
- `LEARNING_LOG.md` — project notes & skills log

Design principle: **mechanism in code, policy in config** — a tiny fixed engine; every
behaviour lives in each agent's `config.json`; new abilities are opt-in modules.
