# The Claude skill behind AICHAT_LAB

This lab is maintained by a **reusable AI skill** — a compact set of instructions that lets a
capable AI assistant (here, Claude) continue the project on any machine without re-deriving its
history from chat. The idea any reader can reuse: **put the "how to safely continue this
project" knowledge in version-controlled instructions, not in a human's head or a chat log.**

## What a "skill" is here
A skill is a short Markdown document (`SKILL.md`) with:
- a **description** that tells the assistant *when* to load it ("resume AICHAT_LAB"),
- the **source of truth** (this GitHub repo) and how to stay in sync,
- the **architecture** and **hard rules** for changing the code safely,
- a **State** block — the single place that records where the project actually is.

When the human says *"continue AICHAT_LAB"*, the assistant loads the skill, pulls the repo,
reads the design docs, checks the `VERSION` file + State, and resumes — no guessing.

## Why it works (transferable principles)
1. **Source of truth is the repo, not the conversation.** Every machine clones/pulls; code is
   identical everywhere, only each machine's `config.json` differs (IPs, paths).
2. **Write-and-test-offline-first.** The assistant writes and runs offline tests (model stubbed)
   *before* the human runs anything live.
3. **One change per run.** Small, reversible steps the human can verify and paste back.
4. **Version everything.** Each working milestone is frozen in `checkpoints/`, the `VERSION`
   file is bumped, and the change is committed and pushed.
5. **New capability = a module + a config flag**, offline-tested — never task logic in the core
   engine.

## The skill (reproduced)
Below is the operating skill, so any AI or human can see exactly how the lab is continued.

~~~markdown
name: aichat-lab
description: Continue the AICHAT_LAB multi-agent lab (Alice & Bob chat, Carlos directs/judges;
  knowledge-graph + shared-graph memory; Aradia ideates) across Mac and Windows over the LAN.
  Source of truth: github.com/Masterskunk/AICHAT_LAB. Use when resuming or extending the lab.

SOURCE OF TRUTH: the GitHub repo. Every machine clones/pulls; code identical everywhere, only
each machine's configs differ. Keep in sync: git add/commit, git pull --rebase, git push.

RESUME CHEAPLY: on "continue AICHAT_LAB" -> pull the repo, read DESIGN.md / README.md /
LEARNING_LOG.md / IDEAS_FROM_AGENTS.md / WINDOWS_HANDOFF.md once, check the VERSION file + State.

ARCHITECTURE (mechanism in code, policy in config):
- Engine agents/<name>/agent.py (chat agents share one identical engine): cfg, log, trace,
  control, memory, graph_recall, think(build_messages), listen/send, respond, direct, report,
  auto, caps, menu.
- Each agent config.json holds ALL policy: model, system(role), options, loop, memory,
  graph_recall, modules, (Carlos) interval/auto{graph,judge,steer}.
- lab.py console: monitor, follow, reset, judge, caps, params, model, control, configure,
  errors, graph, evals.
- logs/: events.jsonl (transcript), trace.jsonl (how), errors.jsonl, control.json,
  graph.json + graph.md (knowledge graph), mem_<name>.txt, aradia_ideas.md, archive/.
- modules/: memory_graph.py (triples -> graph), ideator.py (Aradia), hello.py (demo).
  Toggle via config.modules.

KEY MECHANICS:
- Transport: Alice send (client) <-> Bob listen (HTTP server), turn-based.
- SHARED-GRAPH recall: graph_recall(c) reads graph.json fresh each turn and injects a
  "SHARED KNOWLEDGE already established (build on it, add NEW, do not re-explain)" block.
  Eventually-consistent blackboard; a mid-write read safely skips that turn.
- Carlos: direct (steer via control.json), report/auto (extract triples -> graph; LLM-as-judge).
- Aradia: reads graph.json, asks a high-memory LLM for NEW lab-enhancing concepts, appends
  logs/aradia_ideas.md. Reads-only on shared memory (race-safe); run when others are idle.

HARD RULES:
1. TEST BEFORE SHIP: offline tests (model stubbed); run them, then the human runs live.
2. ONE change per run; the human pastes the result.
3. Menu-driven; colours alice=cyan bob=amber carlos=green aradia=gold; never magenta.
4. VERSION EVERYTHING: snapshot checkpoints/<NAME>/lab at each working milestone, bump VERSION,
   commit + push.
5. Keep DESIGN.md / README.md / LEARNING_LOG.md in sync.
6. New capability = modules/<name>.py (+flag), offline-tested; never task logic in the core.
~~~

The live **State** (what is built, validated, and next) travels with the maintained skill and
with the repo's `VERSION` file and `lab/IDEAS_FROM_AGENTS.md`, so the source of truth and the
instructions never drift apart.
