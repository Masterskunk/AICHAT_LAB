import importlib.util, json
from pathlib import Path
LAB=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("lab",LAB/"lab.py"); lab=importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
s=lab.summarize([{"agent":"alice","event":"send","content":"hi"},{"agent":"bob","event":"reply","content":"yo"},{"agent":"alice","event":"done","turns":40,"reason":"max_turns"}])
assert s["msgs"]["alice"]==1 and s["turns"]==40
(LAB/"logs").mkdir(exist_ok=True); open(LAB/"logs"/"events.jsonl","w").write('{"x":1}\n'); lab.reset()
assert (LAB/"logs"/"events.jsonl").read_text()=="" and list((LAB/"logs"/"archive").glob("*/events.jsonl"))
assert lab.coerce("top_k","40")==40 and lab.coerce("temperature","0.8")==0.8
assert lab.parse_models("NAME ID\nllama3.1:8b a\nphi4 b\n")==["llama3.1:8b","phi4"]
open(LAB/"logs"/"events.jsonl","w").write('{"agent":"alice","event":"send","content":"hola"}\n{"agent":"bob","event":"reply","content":"hi"}\n')
assert "alice: hola" in lab.transcript()
lab.list_models=lambda:["llama3.2:3b","llama3.1:8b"]; assert lab.best_model()=="llama3.1:8b"
print("ALL LAB TESTS PASS: summarize, reset, coerce, parse_models, transcript, best_model")

# --- full config editor helpers ---
_d={}; lab._setdot(_d,"loop.max_turns",5); assert _d["loop"]["max_turns"]==5
lab._setdot(_d,"model","hermes3:8b"); assert _d["model"]=="hermes3:8b"
assert lab._getdot({"stop":{"token":"X"}},"stop.token")=="X"
print("CONFIG-EDITOR TESTS PASS: _setdot/_getdot dotted keys")
