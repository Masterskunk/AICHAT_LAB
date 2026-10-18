import importlib.util, json
from pathlib import Path
LAB=Path(__file__).resolve().parent
def load(n):
    spec=importlib.util.spec_from_file_location(n,LAB/"agents"/n/"agent.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
a=load("alice"); b=load("bob"); cfg=json.load(open(LAB/"agents/alice/config.json"))
(LAB/"logs").mkdir(exist_ok=True); a.write_ctrl({"state":"run","inject":None})
assert a.clean("  hi  there \n")=="hi there"
b.think=lambda h:"OK"; h=[]; assert b.respond("hi",h)=="OK" and len(h)==2
# open chat: no stop token, control=run -> runs to loop.max_turns
sent=[]; a.think=lambda h:"line"; a.post=lambda u,o:(sent.append(o) or {"from":"bob","content":"r"})
a.send("hello"); assert len(sent)==cfg["loop"]["max_turns"]
# anchor toggle
assert a.build_system({"system":"hi","anchor":True}).endswith("plainly.")
assert a.build_system({"system":"hi","anchor":False})=="hi"
# control: stop halts before any post
a.write_ctrl({"state":"stop","inject":None}); calls=[]
a.think=lambda h:"x"; a.post=lambda u,o:(calls.append(o) or {"from":"bob","content":"ok"})
a.send("hi"); assert calls==[]
# control: inject -> turn1 first, turn2 injected, then stop
a.write_ctrl({"state":"run","inject":"STEER"}); posts=[]; seq={"n":0}
def fp(u,o):
    posts.append(o["content"]); seq["n"]+=1
    if seq["n"]==2: a.write_ctrl({"state":"stop","inject":None})
    return {"from":"bob","content":"ok"}
a.think=lambda h:"auto"; a.post=fp; a.send("first")
assert posts[:2]==["first","STEER"], posts
a.write_ctrl({"state":"run","inject":None})
# misc
assert a.is_done("AGREED",{"stop":{"token":"AGREED"}}) and not a.is_done("x",{"stop":{}})
m,t=a.load_modules({"modules":{"hello":True}}); assert "hello" in m
assert "agent=alice" in a.caps_text()
print("ALL ENGINE TESTS PASS: open-chat, anchor toggle, control stop+inject, is_done, loader, caps")

# --- Carlos director decision parser ---
assert a.decide("STOP now")==("stop",None)
assert a.decide("PAUSE")==("pause",None)
assert a.decide("INJECT: ask them about jazz")==("inject","ask them about jazz")
assert a.decide("CONTINUE, looks good")==("continue",None)
import json as _j
assert "carlos" in _j.load(open(LAB/"agents/carlos/config.json"))["name"]
print("CARLOS TESTS PASS: decide() parser, carlos config present")
