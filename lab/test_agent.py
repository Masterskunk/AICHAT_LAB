import importlib.util, json
from pathlib import Path
LAB=Path(__file__).resolve().parent
def load(n):
    spec=importlib.util.spec_from_file_location(n,LAB/"agents"/n/"agent.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
a=load("alice"); b=load("bob"); cfg=json.load(open(LAB/"agents/alice/config.json"))
(LAB/"logs").mkdir(exist_ok=True); a.write_ctrl({"state":"run","inject":None})
assert a.clean("  hi  there \n")=="hi there"
b.think=lambda h:"OK"; h=[]; assert b.respond("hi",h)=="OK"
# memory-aware context: OFF sends all, ON is bounded
hist=[{"role":"user","content":str(i)} for i in range(20)]
assert len(a.build_messages({"system":"S","memory":{"enabled":False}},hist))==21
assert len(a.build_messages({"system":"S","name":"nofile","memory":{"enabled":True,"keep_turns":2}},hist))==5
# memory read/write roundtrip
a.mem_write({"name":"tm"},"a fact"); assert "a fact" in a.mem_read({"name":"tm"})
# log catcher writes a traceback
open(LAB/"logs"/"errors.jsonl","w").close()
try:
    raise ValueError("boom")
except Exception as _e:
    a.logerr("unit", _e)
er=json.loads((LAB/"logs"/"errors.jsonl").read_text().splitlines()[-1])
assert er["where"]=="unit" and "boom" in er["error"] and "Traceback" in er["trace"]
# control + director parser still good
a.write_ctrl({"state":"stop","inject":None}); calls=[]
a.think=lambda h:"x"; a.post=lambda u,o:(calls.append(o) or {"from":"bob","content":"ok"}); a.send("hi"); assert calls==[]
a.write_ctrl({"state":"run","inject":None})
assert a.decide("INJECT: ask about jazz")==("inject","ask about jazz")
print("ALL ENGINE TESTS PASS: memory ctx (off=all,on=bounded), mem rw, log catcher+traceback, control, decide")

import os
mp=a.mem_path({"name":"dd"})
open(mp,"w").close()
a.mem_write({"name":"dd"},"said: hello"); a.mem_write({"name":"dd"},"said: hello")
assert open(mp).read().count("said: hello")==1
msgs=a.build_messages({"system":"S","name":"dd","memory":{"enabled":True,"keep_turns":2}},[{"role":"user","content":"x"}])
assert any("do NOT repeat" in m["content"] for m in msgs)
open(mp,"w").close()
print("REPETITION-FIX TESTS PASS")

assert a.parse_score("SCORE: 4 - varied, not repetitive")[0]==4
assert a.parse_score("nothing numeric")[0] is None
print("AUTO TESTS PASS: parse_score")

assert a._fmt_edges([{"s":"x","rel":"enables","o":"y"}],5)=="x enables y"
_orig=a.graph_recall
a.graph_recall=lambda c:"x enables y"
m=a.build_messages({"system":"S","memory":{}},[{"role":"user","content":"q"}])
assert any("SHARED KNOWLEDGE" in x["content"] and "x enables y" in x["content"] for x in m)
a.graph_recall=_orig
m2=a.build_messages({"system":"S","memory":{},"graph_recall":{"enabled":False}},[{"role":"user","content":"q"}])
assert not any("SHARED KNOWLEDGE" in x["content"] for x in m2)
print("SHARED-GRAPH-RECALL TESTS PASS")
