# AI AGENTS LAB - LEARNING LOG & PORTFOLIO NOTES
(Carlos - hands-on, local, 100% on a Mac with Ollama. For note-taking and as source
material for a CV / portfolio. Non-developer building real agentic-AI systems step by step.)
Last verified against the code and the run logs: 2026-10-17.

## WHAT THIS PROJECT IS
A local multi-agent "lab": small AI agents (Alice, Bob) that talk to each other through a
tiny program I understand line by line, plus a third agent (Carlos) that watches, judges and
directs them. Everything runs offline on my Mac via Ollama (no cloud API keys). Built in tiny,
tested, versioned steps.

## CORE DESIGN PRINCIPLE (the big idea)
MECHANISM IN CODE, POLICY IN CONFIG.
- The engine (agent.py) is a small, fixed program: load config, talk over HTTP, think via the
  LLM, log, enforce a few rules. It almost never changes. 234 lines, standard library only,
  and the SAME file byte-for-byte in all three agent folders.
- Everything tunable lives in each agent's config.json: which model, its role, creativity
  settings, turn limits, stop rules, memory on/off, etc.
- New abilities are optional MODULES turned on/off by a config flag. The engine stays tiny.
Result: I change behaviour by editing a config or flipping a switch - not by rewriting code.
Proof it holds: Alice, Bob and Carlos are three different agents running one identical program.

## HOW IT WORKS (plain words)
- TRANSPORT: Alice "send" drives the conversation, Bob "listen" answers, over local HTTP
  (Alice :9001, Bob :9002). One message at a time, strictly turn-based.
- THINKING: each turn the agent sends its role + the conversation to the local LLM (Ollama) and
  gets one reply back. The model itself is stateless.
- ANCHOR: when config.anchor is true the engine appends a fixed paragraph to the role telling
  the agent to make ONE concrete point per turn and avoid grandiose or cosmic language.
- MEMORY (within a session): with memory.enabled the prompt is role + my notes file
  (logs/mem_<name>.txt) + only the last keep_turns*2 messages, instead of the whole chat.
  A note is appended every turn. With memory off, the whole history is re-sent and the prompt
  grows every turn.
- CONTROL CHANNEL: logs/control.json (run / pause / stop / inject). The sender polls it every
  turn; pause blocks in a 1-second loop; an injected line is used once and cleared; a stop
  resets the file back to run. Both a human (lab.py 8) and Carlos write it.
- CARLOS (director/judge): every 20 s he reads the transcript (last 20 lines), once at least 4
  messages exist, and replies CONTINUE / PAUSE / STOP / INJECT: <line>, which the engine turns
  into a control.json write. The judge (lab.py 4) is separate: it picks the best model installed
  and rates the chat at temperature 0.
- OBSERVABILITY: events.jsonl (the transcript / WHAT), trace.jsonl (prompt size, timing,
  decisions / HOW), errors.jsonl (exception + traceback). Colour console: Alice cyan, Bob amber,
  Carlos green.
- CONTROL PANEL (lab.py, 10 options): 1 monitor, 2 follow live, 3 reset (archive logs),
  4 judge + AI rating, 5 caps, 6 LLM parameters, 7 model, 8 live control, 9 configure any field,
  10 errors + tracebacks.

## WHAT I'VE BUILT / LEARNED (milestones)
1. A reliable two-agent message pipe over HTTP (the "agent loop": observe -> think -> act).
2. Config-driven design: separated the fixed engine from all tunable policy.
3. A menu UI so I never memorise commands; colour output tuned for readability.
4. A trace/debug facility that shows what each agent is doing and why.
5. A module system (capabilities toggled on/off in config).
6. Goal + stop conditions enforced in code (not trusted to the model).
7. Live LLM parameter control (temperature, top_k, top_p, repeat_penalty, num_predict, seed).
8. Model swapping per agent; learned that different models reduce "echo chamber" mirroring.
9. A guessing game: secret grounded in config, WIN detected in CODE (a referee), not the model.
   Learned small models answer badly until temperature=0 and the fact is grounded.
10. An AI "judge" that uses the best available model to rate the agents' behaviour.
11. A free-chat mode where two AIs (aware they are AIs) talk about any topic.
12. A third agent, Carlos, as director/judge with a human-override control channel.
13. A log/error catcher across all agents for fast debugging.
14. Simple file-based memory (read notes + recent turns instead of the whole chat).
15. Versioned checkpoints for safe rollback at every working milestone.
16. Offline tests as the gate before any run: test_agent.py and test_lab.py exercise
    build_messages, memory read/write, the log catcher, the control channel, the director
    parser, and the config editor - with the model stubbed, so they cost nothing to run.

## MEASURED RESULTS (2026-10-17, two real runs from the logs)
What bounded memory actually bought, same lab, same models, memory the only difference:

| | memory OFF (13:33-13:42) | memory ON (14:12-14:21) |
|---|---|---|
| messages sent to the model per turn | grew 2 -> 36, linearly | flat at 8 (50 of 55 calls) |
| think time, average | 7.7 s | 7.2 s |
| think time, worst case | 33.0 s | 16.3 s |
| turns completed | 19 | 28 |
| errors | 0 | 0 |

The point is the first row, not the speed: with memory off the prompt grows every turn, so the
cost of turn 30 is nothing like the cost of turn 3, and the run eventually dies of its own
context. With memory on the prompt size stops growing - 1 role + 1 notes block + 6 recent
messages - so a long run costs the same per turn as a short one. Worst-case latency halved as a
side effect.

Director, same two runs: in the first run Carlos decided STOP twice and his stop really did
reach Alice through control.json (she logged finished reason=control_stop after 16 turns) - the
full director -> control channel -> chatter loop works end to end. In the second run he made 15
decisions and all 15 were CONTINUE, so the conversation drifted with no correction and I ended
it myself. A director that only ever says CONTINUE is not steering anything.

## WHAT THE CHECK FOUND (honest limits, open items)
- Memory notes are not summaries. Each note is the agent's own reply cut at 200 characters,
  so the "memory" is a pile of raw sentences - and at least one line in mem_alice.txt is
  duplicated word for word, which means the repetition is now IN the memory, feeding itself.
  A real summarising step (or the graph) is the next honest fix.
- repeat_penalty 1.2 and anchor=true did not stop cross-turn repetition or abstract drift; the
  second run ran off into collective-consciousness and evolutionary-algorithm talk. Sampling
  dials control words inside a turn, not the shape of a conversation across turns.
- No stop token is configured (stop is empty in all three configs), so a chat ends only at
  max_turns 40, Ctrl-C, or a stop written to control.json. is_done() is live code with nothing
  to match.
- referee() and the config "secret" are still in the engine from the guessing-game stage but
  are inactive here (no secret set). Dead weight to either use or remove.
- The log catcher only captures a real traceback when logerr() is called from inside an
  "except" block. The archived errors.jsonl shows one entry with trace "NoneType: None" from
  the old test, which is exactly why test_agent.py now raises inside a try/except. Worth
  remembering: a logger cannot invent a traceback that Python never produced.
- logs/mem_tm.txt is a leftover from the offline test (it uses an agent named "tm"). Harmless;
  reset() empties it but does not delete it.
- Carlos has a port (9003) in his config but never listens - he communicates only by writing
  control.json. Correct, and worth knowing before looking for a server that isn't there.

## CONCEPTS / TECHNOLOGIES I AM LEARNING HANDS-ON (CV-relevant)
- Agentic AI: the agent loop, tool use, multi-agent systems, agent-to-agent (A2A) messaging.
- Local LLMs with Ollama (llama3.1/3.2, hermes3, qwen2.5, deepseek-r1); model selection trade-offs.
- Prompt engineering and LLM sampling parameters; grounding and determinism.
- LLM evaluation ("LLM-as-judge") and its limits (subjective, not ground truth).
- Orchestration & human-in-the-loop control of autonomous processes.
- Context-window economics: bounded prompts vs linear growth, measured in the trace log.
- Memory systems: session context, simple notes memory; next: knowledge-graph memory and
  vector/RAG memory (symbolic vs vector).
- Software practice as a non-dev: config-driven architecture, modularity, unit testing offline,
  observability/logging/tracing, version control / rollback, portability across machines.
- Related tracks: Python from scratch; Terraform/OpenTofu + Docker + Kubernetes for deploying
  agents; RAG with LangChain; Raspberry Pi + Mac + Windows home AI cluster.

## CURRENT STATE (verified 2026-10-17)
A working 3-agent lab (AICHATBASIC), memory ON, log catcher clean (errors.jsonl empty).
- alice hermes3:8b :9001 | bob llama3.1:8b :9002 | carlos llama3.1:8b (writes control.json only)
- chat agents: temperature 0.6, top_k 40, top_p 0.9, repeat_penalty 1.2, num_predict 200,
  seed 0, num_ctx 4096, keep_alive 5m, max_turns 40, auto_delay 2 s, anchor on,
  memory on with keep_turns 3
- carlos: temperature 0.3, num_predict 60, interval 20 s, min_before_act 4, anchor off, memory off
- modules: only modules/hello.py exists, and it is a demo that proves the loader works. No real
  capability module yet.
- Versions saved: VER_1 (first 3-agent chat), WORKING_V1 (+log catcher), WORKING_V2 (+simple memory).
- The live code is identical to WORKING_V2 except two files: README.md (rewritten to describe
  the 3-agent lab) and test_agent.py (the traceback fix above). So there is nothing new to
  checkpoint yet - the next version should be cut when the first real module lands.

Next: Carlos builds a KNOWLEDGE GRAPH of the conversation (concepts as nodes, relations as
edges) to recall collective knowledge and stop the agents from repeating themselves. Design is
in lab/IDEAS_GRAPH_MEMORY.md: extract (subject, relation, object) triples per message, store in
logs/graph.json, query the graph before a reply and inject the facts as grounding. This is also
the direct answer to the duplicated-memory problem found above.

## ONE-LINE SUMMARY (for a CV)
"Self-taught, hands-on builder of local multi-agent AI systems (Ollama, Python): designed a
config-driven agent engine with bounded memory, live orchestration, LLM-as-judge evaluation,
logging/tracing, versioned releases and offline tests - then measured it, cutting per-turn
prompt growth from linear to flat and worst-case latency from 33 s to 16 s."
