# AICHATBASIC - DESIGN (how it works)

TWO TRUTHS: engine (agent.py, fixed) vs config.json (all policy). Tune via config, not code.

THREE AGENTS: Alice + Bob = chat peers. Carlos = director/judge (watches, does not chat).

TRANSPORT: Alice `send` (client, drives) <-> Bob `listen` (HTTP server, answers). One msg at a time.

TURN LOOP (send), each turn:
  1 check control.json (pause/stop/inject)
  2 compose: turn1=opening ; inject waiting=that line ; else think()
  3 send -> receive -> append both to history
  4 stop checks (token/max_turns) -> readable pause

MEMORY (session): the model is stateless. history list is re-sent in full each turn (msgs=N grows).
Lost when the program stops. (Persistent memory = a future module.)

REASONING: think() = system(role + {secret}/anchor) + full history -> Ollama -> reply.

CONTROL CHANNEL: logs/control.json, polled each turn. States run/pause/stop + optional inject.
Both the human (lab.py 8) and Carlos write it; Alice reads it. Decouples director from chatters.

CARLOS (direct): loop -> read events.jsonl transcript -> model -> decide() [CONTINUE/PAUSE/STOP/
INJECT:<line>] -> write control.json. Also judge (lab.py 4, best model rates the chat).

CONSOLE (lab.py): monitor, reset, judge(+AI), caps(3), params(6), model(7), control(8), configure(9).
Reads logs, writes configs+control. Never touches the engine.

RECORD: events.jsonl (transcript / WHAT) + trace.jsonl (prompt size, timing, decisions / HOW). Colour.

MODULES: optional capabilities in modules/<name>.py, toggled by config.modules.<name>.
