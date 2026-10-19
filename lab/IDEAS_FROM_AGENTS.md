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
