# Tutorial idea: GRAPH MEMORY (from the agents' own Oct-17 conversation)

The agents proposed a hybrid memory: neural net (pattern matching) + a KNOWLEDGE GRAPH as an
external, queryable memory. Build it as a module to learn symbolic vs vector memory.

## module: memory_graph (planned)
- Extract facts as TRIPLES from each message: (subject, relation, object).
  e.g. (knowledge_graph, is_a, external_memory)
- Store as a graph in logs/graph.json: nodes = concepts, edges = relations.
- Before a reply, QUERY the graph for facts about the current topic; inject them as grounding.
- Watch the graph grow; agents reuse facts across turns.
- Later: contrast with vector/RAG memory (embeddings) - the neural vs symbolic debate.
Config-driven, offline-tested, same pattern as every module.
