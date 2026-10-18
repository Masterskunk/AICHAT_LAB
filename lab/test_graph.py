import importlib.util, tempfile
from pathlib import Path
LAB=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("mg",LAB/"modules"/"memory_graph.py")
mg=importlib.util.module_from_spec(spec); spec.loader.exec_module(mg)
p=str(Path(tempfile.mkdtemp())/"g.json")   # scratch, outside the connected folder
t=mg.parse_triples("homomorphic_encryption | enables | private_collaboration\n"
                   "reputation_system | mitigates | misaligned_voting\n"
                   "just some prose with no pipes\n"
                   "subject | relation | object\n")
assert len(t)==2, t
a=mg.add_triples(t,p); assert a==(2,4,2), a
a2=mg.add_triples(t,p); assert a2[0]==0 and a2[2]==2
assert "homomorphic_encryption enables private_collaboration" in mg.recall(p)
print("MEMORY_GRAPH TESTS PASS: parse_triples, add_triples (dedup nodes+edges), recall")

# render_mermaid produces a diagram from graph.json
import tempfile as _tf
q=str(Path(_tf.mkdtemp())/"g2.json"); out=str(Path(_tf.mkdtemp())/"g2.md")
mg.add_triples([("a","enables","b"),("b","needs","c")], q)
mg.render_mermaid(q,out)
txt=open(out).read()
assert "graph LR" in txt and "enables" in txt and '["a"]' in txt
print("RENDER TEST PASS: render_mermaid -> mermaid graph")
