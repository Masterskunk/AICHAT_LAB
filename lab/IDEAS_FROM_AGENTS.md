# IDEAS THE AGENTS GENERATED (mined from their Oct-17 chat)
They spontaneously designed a "swarm shared-graph memory". Below = buildable lab modules,
ordered easiest-first. Each fits our rule: a module + a config flag, offline-tested.

## 1. SHARED GRAPH MEMORY  (easy, high value - also fixes the repetition)
A single collective graph.json that BOTH agents read before replying and write to after.
- Before a turn: inject recall() of the shared graph ("known so far: A enables B ...").
- After a turn: extract triples from the new message into the shared graph.
Why: they literally proposed "a shared graph memory space where each agent queries the
swarm's combined intelligence." Also the direct cure for the repetition you saw.

## 2. REPUTATION / TRUST SCORES  (easy, pure code)
Each agent has a trust score (logs/reputation.json). It rises with accepted/endorsed
contributions, falls with rejected ones. Carlos (judge) updates it.
Why: they designed "a trust score for other agents based on past accuracy."

## 3. CONSENSUS BEFORE A GRAPH EDIT  (medium)
A new fact is added to the shared graph only if agents AGREE (simple 2-of-2, later N-of-M
weighted by trust). Conflicts trigger a re-check.
Why: their "transaction protocol where consensus is sought from peer nodes (Paxos/Raft/DPoS)."
Teaches distributed-systems consensus in miniature.

## 4. GRAPH LEDGER / HISTORY  (easy)
Every edit recorded with who proposed it, when, accepted/rejected. graph.json keeps an
edit log. Ties to our versioning theme and to their "immutable transaction history."

## 5. ENDORSEMENTS  (easy, builds on #2)
An agent can "vouch" for another's contribution; endorsements weighted by the endorser's
own reputation. Their "reputation system with agent endorsements."

## 6. SUSPICION / ANOMALY DETECTION  (medium, pure heuristics first)
A suspicion score from behaviour patterns: only ever proposing (never accepting), frequent
offline/online cycling, sudden reputation jumps. Code heuristics first; ML later.
Why: their "suspicion metric beyond raw reputation."

## 7. REPUTATION DECAY / FORGIVENESS  (easy)
Reputation recovers gradually after inactivity instead of dropping to zero - with guards
against gaming by cycling offline. Their "forgiveness buffer with decay curves."

## ADVANCED / ASPIRATIONAL (later, ties to other tracks)
- Federated learning: each node trains a tiny local model, share only weights, aggregate.
- Privacy-preserving sharing: homomorphic encryption / zero-knowledge / secure multi-party.
- Scale the swarm to >2 agents and across machines (Pi/Windows) - ties to M2M + Terraform.
- Put the shared graph in a real DB (Neo4j/Qdrant) provisioned by Tofu - the Level-3 bridge.

## RECOMMENDED ORDER WHEN YOU RETURN
Shared graph memory (#1) -> reputation (#2) -> consensus (#3) -> ledger (#4).
#1 alone makes the agents build on each other instead of repeating, and showcases the graph.

## META-NOTE
The agents re-derived reputation/trust/suspicion repeatedly - a strong signal that
"shared graph + reputation" is the natural, compelling next build for the lab.

## 8. LAN GRAPH-READER / "SCHOLAR" AGENT  (Carlos's idea, 2026-10-18)
Store every graph the agents generate, then run a SEPARATE agent on another LAN machine
(Pi / Windows) that READS those graphs and learns from them - without being in the chat.

How it maps to the lab (all config-driven, same engine):
1. STORE: Carlos already writes graph.json per session (step 2). Keep a history:
   logs/graphs/graph_<date>.json, plus a merged logs/graph.json (the collective knowledge).
2. SERVE over LAN: one agent exposes the graph over HTTP - add a GET /graph route to the
   listen server (or publish graph.json to a shared folder / the GitHub repo).
3. READER agent (new, e.g. "scholar") on another machine: its config peer points at the
   graph host; before answering it fetches the graph and injects recall() as grounding -
   so it "learns from the others" by reusing their established facts. Portability = config
   only (host/url), exactly our rule.
4. SCALE (later): put the shared graph in a real DB (Neo4j/Qdrant) provisioned by Tofu so
   many machines read/write at once. This is the Level-3 bridge to the Terraform track.

Ties together: shared graph memory (#1), A2A messaging, portability (Mac->Pi->Windows),
and the Terraform/DB deployment track. A clean capstone for the lab.

## ================================================================
## BATCH 2 - mined from the 2026-11-04 run (shared-graph recall ON)
## Theme: GRAPH QUALITY & SMART RETRIEVAL (distinct from Batch-1 trust/consensus).
## With recall ON the agents stopped re-explaining basics and instead designed
## how to make the shared graph itself smarter. Ordered easiest-first; each = a
## module + config flag, offline-testable, mechanism-in-core/policy-in-config.
## ================================================================

### B2-1. WEIGHTED EDGES + recall top-k by weight  (EASY, high value)
Give every edge a weight; recall injects the k HEAVIEST edges, not the first k.
Weight = f(times the fact recurred, recency, Carlos judge score). 
Why: they proposed "score edges by frequency of traversal, relevance, and feedback;
recalculate periodically." Directly upgrades our current first-k graph_recall.
Flag: graph_recall.rank = "weight" | "recent" | "first".

### B2-2. PROVENANCE on every triple  (EASY, pure code)
Store who introduced it + turn + timestamp: {s,rel,o, by:"alice", turn:7, ts:...}.
Why: their "capture provenance/source of each node and edge." Lets us SEE who taught
whom - and is the raw data the #8 Windows scholar needs to learn "from" the others.

### B2-3. CONFIDENCE score per fact + low-confidence filter  (EASY)
Each fact carries a confidence (starts low, rises when a second agent restates it,
or from Carlos's judge score). Recall can skip facts below a threshold.
Why: their "confidence level to filter noise when aggregating." 

### B2-4. DIVERSITY / signal-to-noise weighting  (MEDIUM, the anti-echo-chamber)
Weight a fact by how many DISTINCT agents independently stated it, not raw count -
so two agents parroting each other don't inflate it. 
Why: their "signal-to-noise ratio + diversity index to avoid echo chambers." 
*** This is the real cure for the soft repetition still visible in run 1, AND it
becomes essential the moment the Windows scholar makes it 3-4 voices. High priority.

### B2-5. POPULARITY / node mention-count + freshness decay  (EASY)
Count how often each node is referenced; let old untouched facts decay. Recall favours
popular-and-fresh. Why: their "popularity score + last-updated timestamp + volatility."

### B2-6. CARLOS AS GRAPH AUDITOR (self-monitoring meta-agent)  (MEDIUM)
Extend Carlos (already judge) to periodically audit the graph: flag likely-bad edges,
say WHY, and propose pruning. Why: their "self-monitoring meta-AI that reviews its own
inferences and explains the flags." We already have the judge loop - this reuses it.

### B2-7. HUMAN-IN-THE-LOOP edge review in lab.py  (MEDIUM, ties to menu 11)
A console mode where Carlos (you) approve/reject proposed edges; accepted ones gain
confidence, rejected ones are dropped/penalised. Why: their "active-learning loop with
a task-agnostic human-validation interface."

### B2-8. GRAPH ANALYTICS module: community detection + centrality  (MEDIUM/HARD)
A module that runs modularity/community detection and betweenness/eigenvector centrality
on graph.json. "Bridge" (high-centrality) facts get recall priority; communities = auto
topic clusters. Why: their "community detection + centrality on the graph to find hubs
and emerging clusters." Pure stdlib is doable for small graphs; networkx if allowed.

### B2-9. DOMAIN TAGS / "sentinel" subgraphs  (MEDIUM)
Tag each edge with a topic/domain; render graph.md grouped by domain; let recall focus a
chosen domain. Why: their "sentinel domains / subgraphs monitored for emerging signals."

### B2-10. EXPOSE THE GRAPH VIA AN API for external agents  (= MISSION #8)
Serve graph.json (or a query endpoint) over HTTP so another LAN agent can read/query it.
Why: they explicitly proposed "expose our graph via an API so other AIs query the shared
space - a conversational web." THIS IS EXACTLY the Windows-scholar mission. The agents
independently re-derived our own next milestone -> strong signal it's the right build.

### NOTE ON METHOD
These are "understand = facts in context (retrieval)", not weight training - same stance
as mission #8. B2-1/2/3 are tiny upgrades to the EXISTING graph_recall + Carlos extractor;
B2-4 + B2-10 are what make a multi-machine swarm actually work without echo-chambers.

## ================================================================
## BATCH 3 - generated BY Aradia (qwen3:14b) reading the graph, 2026-11-05
## The ideator read the 91-fact graph and proposed upgrades. Below: the ones that are
## NEW (not already in Batch 1/2) and feasible for this local lab, with a feasibility tag.
## Several of Aradia's ideas (edge weighting, decay, volatility, meta-feedback, community
## maps) simply re-confirm Batch-2 items - a strong signal those are the right next builds.
## ================================================================

### B3-1. Temporal Graph Snapshots  (FEASIBLE - EASY, build next)
Carlos saves a dated copy logs/graphs/graph_<ts>.json each session (he already writes graph.json).
Lets us diff the graph over time and see what the swarm learned. Tiny: one write in report/auto.

### B3-2. Graph-Driven Prompt Expansion  (FEASIBLE - EASY/MED)
Make recall TOPIC-AWARE: instead of the first/heaviest k edges, inject the graph neighbours of
the current turn's topic. Extends graph_recall; pairs naturally with B2-1 (weights).

### B3-3. Ontology Conflict Resolution  (FEASIBLE - MED, pure heuristic first)
Detect contradictions: same subject+relation pointing at different objects, or near-duplicate
nodes. A modules/graph_audit.py that lists conflicts for Carlos (ties to B2-6 Carlos-as-auditor).

### B3-4. Meta-Feedback Loop Analyzer  (FEASIBLE - MED)
We already log judge SCORES and graph node/edge counts. Plot score vs graph growth over a run to
see whether a richer shared graph actually improves conversation quality. A lab.py evals view.

### B3-5. Graph Query command in lab.py  (FEASIBLE - MED; from Aradia's "Interactive Query Builder")
A console command to query the graph by keyword (reuses the MCP server's query()). Not a GUI - a
text query in lab.py 11/12. Gives humans the same "ask the graph" power the agents have.

### Deferred (not yet feasible / need more signal)
- Graph-Based User Intent Prediction, Subdomain Volatility Predictor: need time-series history we
  don't have yet - revisit after B3-1 (snapshots) gives us data over time.
- Dynamic Contextual Graph Layers: overlaps B3-2; fold in there.
- Cross-Agent Memory Sync: already essentially DONE by the shared graph + recall.

### RECOMMENDED BUILD ORDER FROM HERE
B3-1 snapshots (trivial, unlocks time-series) -> B2-1 weighted edges -> B3-2 topic-aware recall
-> B2-4 diversity weighting (anti-echo-chamber, matters once Danaris/Colossus join).
