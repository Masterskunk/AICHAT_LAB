# AICHATBASIC - two AIs chatting freely

Two local Ollama agents (Alice, Bob) that KNOW they are AIs and talk about any topic.
YOU start them and stop them (Ctrl-C). All on your Mac, config-driven, no code editing needed.

## Run
One venv per agent (one time):
  python3 -m venv agents/alice/.venv ; python3 -m venv agents/bob/.venv
Terminal 1 (Bob):  source agents/bob/.venv/bin/activate   && python3 agents/bob/agent.py   -> 2 (listen)
Terminal 2 (Alice):source agents/alice/.venv/bin/activate && python3 agents/alice/agent.py -> 3 (talk), type a topic
Terminal 3 (watch/score): python3 lab.py  -> 2 monitor live, 4 judge, 6 params, 7 model
Stop the chat anytime with Ctrl-C.  Needs Ollama with the model in config (llama3.1:8b).

## Coming next
- web search tool so they can look up topics they don't know (keyless, your Mac's internet).
