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
