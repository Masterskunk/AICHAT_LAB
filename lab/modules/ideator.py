"""Ideator module: read the lab's shared knowledge graph and propose NEW concepts
to enhance the lab. Pure, testable functions (+ TOOLS entry). Enable via
config.modules.ideator=true. The agent (Aradia) only READS graph.json and WRITES
logs/aradia_ideas.md - it never edits the graph, so it is race-safe even if the
chat agents are running (intended use: run it when they are idle)."""
import time

SYSTEM=("You are Aradia, a reflective research agent in a LOCAL multi-agent AI lab "
 "(agents Alice and Bob chat; Carlos judges and builds a knowledge graph). You are given "
 "the lab's shared KNOWLEDGE GRAPH - the facts the agents have established. Your job is to "
 "INVENT new concepts, mechanisms, modules or experiments that are NOT already in the graph "
 "and that would make THIS lab better: new agent capabilities, memory/graph improvements, "
 "coordination or evaluation ideas. Be concrete and buildable on a local Ollama setup. "
 "Output ONLY lines in the form:  <concept name> | <one sentence on why it helps the lab>  "
 "Do not restate existing facts. No preamble, no closing remarks.")

def graph_to_text(graph, limit=300):
    edges=(graph or {}).get("edges",[])[:limit]
    return "\n".join(f'{e.get("s","")} {e.get("rel","")} {e.get("o","")}' for e in edges)

def build_prompt(graph, n=8):
    facts=graph_to_text(graph); ne=len((graph or {}).get("edges",[]))
    user=(f"SHARED KNOWLEDGE GRAPH ({ne} facts):\n{facts}\n\n"
          f"Propose {n} NEW concepts to enhance this lab, each as:  name | why.  "
          f"They must go BEYOND the facts above, not restate them.")
    return SYSTEM, user

def parse_concepts(text):
    out=[]
    for ln in (text or "").splitlines():
        ln=ln.strip().lstrip("0123456789.)-*#> \t").strip()
        if "|" not in ln: continue
        name,_,why=ln.partition("|")
        name=name.strip().strip("*`"); why=why.strip()
        if 3<=len(name)<=90:
            out.append((name,why))
    return out

def format_entry(concepts, model="?"):
    ts=time.strftime("%Y-%m-%d %H:%M:%S")
    lines=[f"\n## Aradia ideas {ts}  (model={model}, {len(concepts)} concepts)"]
    for name,why in concepts:
        lines.append(f"- **{name}** - {why}" if why else f"- **{name}**")
    return "\n".join(lines)+"\n"

def ideate(graph, llm_fn, model="?", n=8):
    """graph: dict. llm_fn(system,user)->text. Returns (concepts list, entry text)."""
    system,user=build_prompt(graph,n)
    raw=llm_fn(system,user)
    concepts=parse_concepts(raw)
    return concepts, format_entry(concepts, model)

def on_start(cfg): pass
def _run(args,cfg): return "ideator ready"
TOOLS={"ideator":_run}
