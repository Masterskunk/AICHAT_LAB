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
