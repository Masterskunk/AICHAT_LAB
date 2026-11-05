"""Offline test for the ideator module. Stubs the LLM - no Ollama needed."""
import json, importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("ideator",Path("modules/ideator.py"))
I=importlib.util.module_from_spec(spec); spec.loader.exec_module(I)

# messy LLM output: numbering, bullets, a junk line, a no-pipe line, good lines
STUB=("""Here are ideas:
1. Edge Decay Scheduler | old facts lose weight so stale knowledge fades
- Confidence Voting | a fact gains confidence when a second agent restates it
2) Graph Diff Viewer | show what changed in the graph between two sessions
just some filler without a pipe
* Cross-Agent Citations | track which agent first introduced each fact
**Topic Sentinels** | watch chosen domains for new incoming facts
x |""")   # trailing junk (empty name side / empty why) -> name 'x' too short, dropped

def stub_llm(system,user): 
    assert "KNOWLEDGE GRAPH" in user and "name | why" in user  # prompt shape
    return STUB

# 1) parse filters junk, keeps good concept|why pairs
c=I.parse_concepts(STUB)
names=[n for n,_ in c]
assert "Edge Decay Scheduler" in names and "Confidence Voting" in names
assert "Cross-Agent Citations" in names and "Topic Sentinels" in names
assert all("|" not in n for n,_ in c)                 # pipe stripped from names
assert "x" not in names                               # too-short name dropped
assert "just some filler without a pipe" not in names # no-pipe line dropped
assert len(c)==5, f"expected 5 concepts, got {len(c)}: {names}"
print("PARSE OK ->", names)

# 2) end-to-end ideate() against the REAL graph.json
g=json.loads(Path("logs/graph.json").read_text())
concepts,entry=I.ideate(g, stub_llm, model="llama3.1:8b", n=8)
assert len(concepts)==5
assert entry.startswith("\n## Aradia ideas") and "llama3.1:8b" in entry
assert "**Edge Decay Scheduler**" in entry and "- old facts lose weight" in entry
print("IDEATE OK -> entry has", len(concepts), "concepts, header + markdown bullets")

# 3) empty graph still builds a valid prompt (no crash)
s,u=I.build_prompt({"nodes":[],"edges":[]},n=3)
assert "0 facts" in u and "Propose 3" in u
print("EMPTY-GRAPH PROMPT OK")

print("\nALL IDEATOR TESTS PASS")
