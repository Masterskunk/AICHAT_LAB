#!/usr/bin/env python3
"""Aradia - reflective IDEATOR agent. Reads the shared knowledge graph and proposes
NEW concepts to enhance the lab (appends logs/aradia_ideas.md). No chat, no HTTP.
Run it when Alice/Bob/Carlos are idle. No args = MENU."""
import json, sys, time, platform, urllib.request, importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent; CFG=HERE/"config.json"
LOGS=HERE.parent.parent/"logs"; EVENTS=LOGS/"events.jsonl"; ERR=LOGS/"errors.jsonl"
MODDIR=HERE.parent.parent/"modules"
_R="\033[0m"; _DIM="\033[2m"; GOLD="\033[1;38;5;220m"; _REDC="\033[1;91m"
def cfg(): return json.loads(CFG.read_text())
def log(event,**kw):
    LOGS.mkdir(parents=True,exist_ok=True)
    rec={"ts":time.strftime("%H:%M:%S"),"agent":cfg().get("name","aradia"),"event":event,**kw}
    EVENTS.open("a").write(json.dumps(rec)+"\n")
def logerr(where,e):
    import traceback
    LOGS.mkdir(parents=True,exist_ok=True)
    rec={"ts":time.strftime("%H:%M:%S"),"agent":"aradia","where":where,"error":str(e),"trace":traceback.format_exc()[-1000:]}
    ERR.open("a").write(json.dumps(rec)+"\n"); print(f"{_REDC}[ERROR {where}] {e}{_R}")
def load_ideator():
    spec=importlib.util.spec_from_file_location("ideator",MODDIR/"ideator.py")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def read_graph():
    try: return json.loads((LOGS/"graph.json").read_text())
    except Exception: return {"nodes":[],"edges":[]}
def chat(system,user):
    c=cfg(); body={"model":c["model"],"messages":[{"role":"system","content":system},{"role":"user","content":user}],
                   "stream":False,"options":c.get("options",{}),"keep_alive":c.get("keep_alive","5m")}
    req=urllib.request.Request(c["ollama"]+"/api/chat",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=300) as r: return json.loads(r.read())["message"]["content"].strip()
def caps():
    c=cfg(); ic=c.get("ideator",{})
    print(f'{GOLD}agent={c["name"]} role=ideator model={c["model"]} '
          f'platform={platform.system()}/{platform.machine()} '
          f'reads=logs/graph.json writes=logs/{ic.get("outfile","aradia_ideas.md")} n={ic.get("n",8)}{_R}')
def ideate():
    c=cfg(); g=read_graph()
    if not g.get("edges"):
        print(f"{GOLD}graph is empty - run Carlos (report/auto) first so I have something to read{_R}"); return
    ic=c.get("ideator",{}); n=int(ic.get("n",8)); outfile=LOGS/ic.get("outfile","aradia_ideas.md")
    print(f"{_DIM}reading {len(g['edges'])} facts, asking {c['model']} for {n} new concepts...{_R}")
    try:
        mod=load_ideator(); concepts,entry=mod.ideate(g, chat, model=c["model"], n=n)
    except Exception as e:
        logerr("ideate",e); return
    outfile.parent.mkdir(parents=True,exist_ok=True)
    with outfile.open("a") as f: f.write(entry)
    log("ideate",concepts=len(concepts),model=c["model"])
    print(f"{GOLD}{entry}{_R}{_DIM}appended {len(concepts)} concepts -> logs/{outfile.name}{_R}")
def menu():
    while True:
        print(f"""
{GOLD}========== ARADIA  (reflective ideator) =========={_R}
  {GOLD}1{_R}) caps      what I am / what I read & write
  {GOLD}2{_R}) ideate    read the graph, propose NEW concepts to enhance the lab
  {GOLD}0{_R}) quit      (or type q)
{_DIM}Run me when Alice/Bob/Carlos are idle. Ctrl-C to abort a run.{_R}""")
        ch=input("choose > ").strip().lower()
        try:
            if ch=="1": caps()
            elif ch=="2": ideate()
            elif ch in ("0","q","quit","exit"): break
            else: print("pick a number")
        except Exception as e: logerr("menu",e)
if __name__=="__main__":
    a=sys.argv[1:]
    try:
        if not a: menu()
        elif a[0]=="caps": caps()
        elif a[0]=="ideate": ideate()
        else: print(__doc__)
    except KeyboardInterrupt: print("\nbye")
