"""Offline tests for Aradia's console helpers (no Ollama)."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("aradia",Path("agents/aradia/agent.py"))
A=importlib.util.module_from_spec(spec); spec.loader.exec_module(A)

# parse_tags: pull names out of an /api/tags payload
tags={"models":[{"name":"qwen3:14b"},{"name":"qwen2.5:14b-instruct"},{"bad":"x"},{"name":"phi4:latest"}]}
names=A.parse_tags(tags)
assert names==["qwen3:14b","qwen2.5:14b-instruct","phi4:latest"], names
print("parse_tags OK ->",names)

# pick_model: digit picks from list; text used literally; blank/out-of-range keep current
assert A.pick_model("1",names,"old")=="qwen3:14b"
assert A.pick_model("3",names,"old")=="phi4:latest"
assert A.pick_model("",names,"old")=="old"              # blank keeps
assert A.pick_model("9",names,"old")=="old"             # out of range keeps
assert A.pick_model("llama3.2:3b",names,"old")=="llama3.2:3b"  # typed name
print("pick_model OK")

# coerce: blank keeps; else typed to kind; bad input keeps
assert A.coerce("int","",8)==8
assert A.coerce("int","12",8)==12
assert A.coerce("float","0.5",0.8)==0.5
assert A.coerce("bool","on",False)==True
assert A.coerce("bool","off",True)==False
assert A.coerce("int","abc",8)==8                       # garbage keeps
print("coerce OK")

print("\nALL ARADIA CONSOLE TESTS PASS")
