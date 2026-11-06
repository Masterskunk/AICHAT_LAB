# GIT guide for AICHAT_LAB (Mac + Windows + Pi)

The GitHub repo is the **single source of truth**. Every machine clones the SAME repo; the code is
identical everywhere, only each machine's `config.json` files differ (models, LAN IPs). This guide
covers the everyday flow, the cross-machine setup, and how to work on a fork/branch.

## 1. One-time setup on a machine
    git clone https://github.com/Masterskunk/AICHAT_LAB.git
    cd AICHAT_LAB
Install Git + Ollama first. Pull the models that machine will run (e.g. `ollama pull llama3.2:3b`).

## 2. The everyday flow (do this every session)
    git pull --rebase          # get changes made on the other machines FIRST
    # ...work: edit code/config, run agents...
    git add <the files you changed>     # stage INTENTIONALLY (see note on logs below)
    git commit -m "clear message: what + why"
    git push
Always `pull --rebase` before you start, and `push` when you finish, so the three machines stay in
sync and never clobber each other.

## 3. Stage on purpose - don't sweep
Prefer `git add <paths>` over `git add -A`. The `logs/` folder churns every run (transcripts,
graph, memory) and usually should NOT be committed except when snapshotting a milestone. Example:
    git add lab/agents lab/modules lab/tools README.md
This keeps commits clean and the public history readable.

## 4. Which machine changes what
- Code (`agents/*/agent.py`, `modules/`, `tools/`, `lab.py`) is identical on all machines - change it
  on any machine, commit, push, and `pull --rebase` on the others.
- Config differs per machine and is committed as the default; each machine may keep local tweaks:
  - Mac: Alice/Bob/Carlos/Aradia; runs `tools/graph_server.py` to publish the graph.
  - Windows (Danaris): set `graph_url` to the Mac's LAN IP.
  - Pi (Colossus): set `mcp_url`/`chat_peer` to the Mac's LAN IP.
  Find the Mac IP: `ipconfig getifaddr en0`.

## 5. Branches and forks (isolating new work)
A **branch** is a parallel line of work inside the same repo - cheap, and you can merge it into
`main` later. Use one when you want `main` (the public showcase) to stay stable while you build.
    git checkout -b swarm-agents      # create + switch to the branch
    git add ... && git commit -m "..."
    git push -u origin swarm-agents   # publish the branch
    # later, when happy:  git checkout main ; git merge swarm-agents ; git push
A **fork** is a full copy of the repo under another owner/account - use it when someone else wants
their own line of the project. Fork someone else's repo with `gh repo fork <owner>/<repo>`.
A **separate repo** is a brand-new independent project:
    gh repo create AICHAT_LAB_SWARM --public --source=. --remote=swarm --push

## 6. The .lock / "File exists" gotcha (connected-folder sandboxes)
If `git commit`/`pull` fails with a `.lock` "File exists" error, git couldn't delete its own lock
file because deletion isn't permitted in that folder. Grant delete permission for the folder and
retry - don't keep re-running the same failing command.

## 7. Versioning milestones
When a milestone works: freeze it in `checkpoints/<NAME>/lab`, bump `lab/VERSION`, update the docs,
then commit + push. Restore a checkpoint by copying it back over `lab/`.
