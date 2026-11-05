"""memory_graph: turn conversation facts into a knowledge graph.
A TRIPLE is (subject, relation, object), written by the model as:  A | relation | B
Nodes = concepts, edges = relations. Stored in logs/graph.json. Pure/testable; no Ollama here."""
import json, re
from pathlib import Path

NAMES={"alice","bob","carlos"}
_PRON={"here","there","this","that","it","they","we","you","i","he","she","them","these","those","one","something"}
def _ok(term):
    w=term.split()
    return 2<=len(term)<=40 and 1<=len(w)<=5 and term.lower() not in _PRON
def _term(x):
    x=x.strip()
    x=re.sub(r'^\s*\d+[\.\)]\s*','',x)
    x=re.sub(r'^[-*\u2022]\s*','',x)
    return x.strip().strip('"').strip("'").strip()
def parse_triples(text):
    """Lenient parse of model output: keep only clean 'A | rel | B' lines."""
    out=[]
    for ln in (text or "").splitlines():
        parts=[p.strip() for p in ln.split("|")]
        if len(parts)==3:
            s,rel,o=_term(parts[0]),parts[1].strip(),_term(parts[2])
            if not (s and rel and o): continue
            if (s.lower(),o.lower())==("subject","object"): continue   # skip a header line
            if not (_ok(s) and _ok(o)): continue                       # drop pronouns & sentence-fragments
            if s.lower() in NAMES or o.lower() in NAMES: continue       # ideas, not who-said-what
            if any(("'" in t) or t.endswith((".","!","?")) for t in (s,o)): continue
            out.append((s,rel,o))
    return out

def load_graph(path):
    try: return json.loads(Path(path).read_text())
    except Exception: return {"nodes":[],"edges":[]}

def save_graph(g,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(g,indent=2))

def add_triples(triples,path):
    """Add triples, de-duplicating nodes and edges case-insensitively. Returns (added,nodes,edges)."""
    g=load_graph(path)
    nodes={n.lower():n for n in g.get("nodes",[])}
    seen={(e["s"].lower(),e["rel"].lower(),e["o"].lower()) for e in g.get("edges",[])}
    added=0
    for s,rel,o in triples:
        nodes.setdefault(s.lower(),s); nodes.setdefault(o.lower(),o)
        k=(s.lower(),rel.lower(),o.lower())
        if k not in seen:
            g["edges"].append({"s":s,"rel":rel,"o":o}); seen.add(k); added+=1
    g["nodes"]=sorted(nodes.values())
    save_graph(g,path)
    return added,len(g["nodes"]),len(g["edges"])

def recall(path,limit=20):
    """Compact text of what's known so far, for injecting back to the agents."""
    g=load_graph(path)
    return "\n".join(f'{e["s"]} {e["rel"]} {e["o"]}' for e in g.get("edges",[])[:limit])


def render_mermaid(path, out):
    """Write graph.json as a Mermaid diagram (graph.md) you can open to see the picture."""
    g=load_graph(path); idx={n:f"n{i}" for i,n in enumerate(g.get("nodes",[]))}
    lines=["```mermaid","graph LR"]
    for e in g.get("edges",[]):
        a=idx.get(e["s"],"nx"); b=idx.get(e["o"],"ny")
        lines.append(f'  {a}["{e["s"]}"] -->|{e["rel"]}| {b}["{e["o"]}"]')
    lines.append("```")
    Path(out).write_text("# Knowledge graph (auto-built by Carlos)\n\n"+"\n".join(lines)+"\n")
    return len(g.get("edges",[]))
