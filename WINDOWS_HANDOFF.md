# WINDOWS HANDOFF — continue the AICHAT_LAB on the Windows machine

Goal: build the next ("fifth") agent on Windows (RTX 4070) and join it to the lab over the LAN —
most likely the LAN graph-reader / "danaris" from IDEAS_FROM_AGENTS.md #8.

## 1. Get the project (the skill is already on your Claude account)
On Windows, install Git + Ollama, then:
    git clone https://github.com/Masterskunk/AICHAT_LAB.git
    cd AICHAT_LAB
    ollama pull llama3.1:8b    (and any models you want)
Open the Claude desktop app on Windows, "Add folder" -> the cloned AICHAT_LAB folder.

## 2. Bootstrap the Claude session (paste this)
Use skill `aichat-lab`. Read lab/DESIGN.md, lab/README.md, lab/INDEX? , LEARNING_LOG.md and
lab/IDEAS_FROM_AGENTS.md once. We are on WINDOWS now; the Mac runs Alice/Bob/Carlos. I want to
build the fifth agent here and connect it to the others over the LAN. Follow the lab's rules:
mechanism in code / policy in config, one change per run, offline-test first, version each step.

## 3. Windows specifics (only configs change — the engine is pure stdlib, portable)
- venv per agent:   py -m venv .venv   then   .venv\Scripts\activate   (vs mac: source .venv/bin/activate)
- run an agent:     python agents\<name>\agent.py
- LAN wiring (so Windows <-> Mac agents talk):
    * On the LISTENER's config set  "host": "0.0.0.0"  (not 127.0.0.1) so the LAN can reach it.
    * On the caller set "peer_url": "http://<OTHER-MACHINE-LAN-IP>:<port>".
    * Find IPs:  Mac -> `ipconfig getifaddr en0` ;  Windows -> `ipconfig` (IPv4 Address).
    * Allow the port through Windows Defender Firewall (inbound rule for the agent's port).
- Ollama must be running on whichever machine hosts each agent's model.

## 4. Keep GitHub in sync (source of truth across machines)
After changes on either machine:
    git add -A && git commit -m "..."
    git pull --rebase    (get the other machine's changes)
    git push
Each machine clones/pulls the same repo; configs differ per machine (IPs), code stays identical.

## 5. Where things are
lab/ = live project (agents, lab.py console, modules, tests, docs).
checkpoints/ = frozen working versions (restore: copy checkpoints/<VER>/lab over lab/).
LEARNING_LOG.md = notes + skills log. IDEAS_FROM_AGENTS.md = the agent-generated roadmap (incl. #8 LAN reader).

## 6. THE DANARIS IS NOW BUILT (2026-11-05) — exact steps to test it
The "fifth agent" is ready as **`agents/danaris/`**. It is the same ideator engine as Aradia,
but it reads the graph REMOTELY over the LAN (config `graph_url`) and writes its ideas locally.
"Understand" here = read the shared graph into context (retrieval), not weight training.
It needs only: Ollama running on Windows + the Mac publishing its graph. 8 GB VRAM (RTX 4070)
fits `llama3.1:8b`; num_ctx is 8192 to stay in VRAM.

### A. On the MAC — publish the graph over the LAN
    cd ~/Desktop/AICHATBASIC/lab
    ipconfig getifaddr en0            # note this IP, e.g. 192.168.1.23
    python3 tools/graph_server.py     # serves logs/graph.json on 0.0.0.0:8800 (leave running)
If macOS prompts to allow incoming connections for python, click Allow.
(Keep Carlos running report/auto so the graph stays fresh; the server always serves the latest file.)

### B. On WINDOWS — point the danaris at the Mac and run it
    git clone https://github.com/Masterskunk/AICHAT_LAB.git   (or: git pull)
    cd AICHAT_LAB\lab
    ollama pull llama3.1:8b
Edit `agents\danaris\config.json` -> set  "graph_url": "http://<MAC-LAN-IP>:8800/graph.json"
Then:
    python agents\danaris\agent.py
      3) model   -> pick your Windows model (llama3.1:8b)
      2) ideate  -> fetches the Mac's graph over the LAN, writes logs\danaris_ideas.md

### C. Verify the LAN hop first (if ideate says "could not fetch")
    curl http://<MAC-LAN-IP>:8800/graph.json      # should print JSON
If it hangs: Mac firewall is blocking 8800, the server isn't running, or the IP is wrong
(re-check `ipconfig getifaddr en0`). Both machines must be on the same network.

### Why this matters
This is the first agent that learns from the swarm WITHOUT being in the conversation - it reads
the collective knowledge graph the others built and contributes new ideas back. Same mechanism,
different machine: the proof that the shared-graph memory crosses the LAN.
