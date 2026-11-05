# AICHATBASIC - two AIs chat, a third (Carlos) directs

Local Ollama agents on your Mac. Config-driven, menu-run, versioned for rollback.

## Agents
- alice, bob : chat peers (alice=hermes3:8b, bob=llama3.1:8b)
- carlos     : director/judge - watches and steers (CONTINUE/PAUSE/STOP/INJECT)

## Run (each agent from its own folder, its own venv)
  cd agents/bob    && python3 -m venv .venv && source .venv/bin/activate && python3 agent.py   # 2 listen
  cd agents/alice  && python3 -m venv .venv && source .venv/bin/activate && python3 agent.py   # 3 talk (type topic)
  cd agents/carlos && python3 -m venv .venv && source .venv/bin/activate && python3 agent.py   # 6 direct (auto-steer)
Console (lab root):  python3 lab.py
  1 monitor  2 follow  3 reset  4 judge(+AI)  5 caps  6 params  7 model  8 control  9 configure  10 errors

## Features
- LOG CATCHER: every exception -> logs/errors.jsonl with traceback; view via lab.py 10.
- MEMORY (simple): memory.enabled reads logs/mem_<name>.txt + last keep_turns instead of the whole chat;
  appends a note each turn. Toggle/keep_turns via lab.py 9.
- CONTROL CHANNEL: logs/control.json (pause/continue/stop/inject) - human (lab 8) or Carlos.
- ANCHOR toggle (config.anchor): grounded vs free-drift.
- TRACE: logs/trace.jsonl (prompt size, timing, decisions).

## Versions (checkpoints/)  - restore: cp -R checkpoints/<VER>/lab/. lab/
- VER_1        first working 3-agent free chat
- WORKING_V1   + log catcher (memory off)
- WORKING_V2   + simple memory (on)

## Next ideas
- memory_graph : facts as (subject,relation,object) triples in a graph (see IDEAS_GRAPH_MEMORY.md)
- web search   : look up topics the agents don't know
