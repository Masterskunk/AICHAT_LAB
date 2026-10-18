#!/usr/bin/env python3
"""AI Chat control panel. Run with no args for the menu."""
import json, sys, time, os, importlib.util
from pathlib import Path
LAB=Path(__file__).resolve().parent
LOG=LAB/"logs"/"events.jsonl"; TRACE=LAB/"logs"/"trace.jsonl"
OLLAMA="http://127.0.0.1:11434"
CTRL=LAB/"logs"/"control.json"
ERR=LAB/"logs"/"errors.jsonl"
def read_ctrl():
    try: return json.loads(CTRL.read_text())
    except Exception: return {"state":"run","inject":None}
def write_ctrl(d):
    CTRL.parent.mkdir(parents=True,exist_ok=True); CTRL.write_text(json.dumps(d))
def director():
    while True:
        st=read_ctrl().get("state","run")
        print(f"\n{_DIM}LIVE conversation control - state={st}{_R}")
        print("  p) pause   c) continue   s) stop   i) inject a line   b) back")
        k=input("> ").strip().lower()
        if k=="p": write_ctrl({**read_ctrl(),"state":"pause"}); print("paused")
        elif k=="c": write_ctrl({**read_ctrl(),"state":"run"}); print("running")
        elif k=="s": write_ctrl({**read_ctrl(),"state":"stop"}); print("stop sent")
        elif k=="i":
            m=input("line to inject > ").strip()
            if m: write_ctrl({**read_ctrl(),"inject":m}); print("will inject next turn")
        elif k in ("b","0",""): break
        else: print("use p/c/s/i/b")
_R="\033[0m"; _DIM="\033[2m"
_AG={"alice":"\033[1;96m","bob":"\033[1;38;5;214m"}
_EV={"send":"\033[1;93m","reply":"\033[1;93m","recv":"\033[1;94m","start":"\033[1;97m","done":"\033[1;97m","error":"\033[1;91m"}
_ARROW={"send":"▶","reply":"▶","recv":"◀"}
def _line(r):
    ag=r.get("agent","");ev=r.get("event","")
    ac=_AG.get(ag,"\033[1;97m");ec=_EV.get(ev,"\033[1;97m");ar=_ARROW.get(ev,"•")
    extra=" ".join(f"{k}={v}" for k,v in r.items() if k not in ("ts","agent","event","content"))
    head=f'{_DIM}{r.get("ts","")}{_R} {ac}{ag.upper():<5}{_R} {ec}{ar} {ev.upper():<6}{_R} {_DIM}{extra}{_R}'
    body=f'\n    {ac}{r["content"]}{_R}' if r.get("content") else ""
    return head+body+("\n" if ev in ("recv","done","error") else "")
def _rows(): return LOG.read_text().splitlines() if LOG.exists() else []
def view(follow=False):
    seen=_rows()
    for l in seen:
        try: print(_line(json.loads(l)))
        except: pass
    n=len(seen)
    if follow:
        print(_DIM+"...following (Ctrl-C to stop)"+_R)
        try:
            while True:
                time.sleep(0.5); cur=_rows()
                for l in cur[n:]:
                    try: print(_line(json.loads(l)))
                    except: pass
                n=len(cur)
        except KeyboardInterrupt: print("stopped")
def reset():
    ts=time.strftime("%Y%m%d-%H%M%S"); dst=LAB/"logs"/"archive"/ts; dst.mkdir(parents=True,exist_ok=True); moved=[]
    for f in (LOG,TRACE,ERR):
        if f.exists() and f.stat().st_size>0: os.rename(f,dst/f.name); moved.append(f.name)
        f.parent.mkdir(parents=True,exist_ok=True); open(f,"w").close()
    write_ctrl({"state":"run","inject":None})
    [open(m,"w").close() for m in LAB.glob("logs/mem_*.txt")]
    print(f"archived {moved or 'nothing'} -> logs/archive/{ts}; logs clean")
def summarize(rows):
    msgs={}; errors=0; turns=0; result="(still open / stopped by you)"
    for r in rows:
        ev=r.get("event"); ag=r.get("agent")
        if ev in ("send","reply"): msgs[ag]=msgs.get(ag,0)+1
        if ev=="error": errors+=1
        if ev=="done": turns=r.get("turns",0); result=f"ended ({r.get('reason','')}) after {turns} turns"
    return {"msgs":msgs,"errors":errors,"turns":turns,"result":result}
INT_KEYS={"top_k","num_predict","seed","num_ctx"}
PARAMS=[("temperature",0.8,"randomness: 0=strict, ~0.8 natural chat, 1=creative (max 2)"),
 ("top_k",40,"top K likely words; lower=safer"),("top_p",0.9,"nucleus cutoff 0-1"),
 ("repeat_penalty",1.2,"discourage repeats (1.0-1.3); higher helps long chats"),
 ("num_predict",200,"max words per turn"),("seed",0,"fixed=repeatable; change for variety"),
 ("num_ctx",4096,"context window in tokens")]
def coerce(k,val): f=float(val); return int(f) if k in INT_KEYS else f
def edit_params():
    name=input("which agent? (alice/bob) > ").strip().lower(); fp=LAB/"agents"/name/"config.json"
    if not fp.exists(): print("no such agent"); return
    d=json.load(open(fp)); opts=d.setdefault("options",{}); names=[n for n,_,_ in PARAMS]
    while True:
        print(f"\n{_AG.get(name,'')}--- {name} parameters ---{_R}")
        for k,base,h in PARAMS: print(f"  {k:<15}= {str(opts.get(k,'(unset)')):<7} {_DIM}base {str(base):<6} {h}{_R}")
        k=input("param to change (Enter=save&exit) > ").strip()
        if not k: break
        if k not in names: print("unknown"); continue
        v=input(f"new value for {k} > ").strip()
        try: opts[k]=coerce(k,v); print(f"{k} set to {opts[k]}")
        except ValueError: print("must be a number")
    d["options"]=opts; open(fp,"w").write(json.dumps(d,indent=2)); print(f"saved -> {name}")
def parse_models(text):
    out=[]
    for i,ln in enumerate(text.splitlines()):
        if i==0 or not ln.strip(): continue
        out.append(ln.split()[0])
    return out
def list_models():
    import subprocess
    try: return parse_models(subprocess.run(["ollama","list"],capture_output=True,text=True,timeout=10).stdout)
    except Exception: return []
def set_model():
    name=input("which agent? (alice/bob) > ").strip().lower(); fp=LAB/"agents"/name/"config.json"
    if not fp.exists(): print("no such agent"); return
    d=json.load(open(fp)); print(f"current model: {d.get('model')}"); models=list_models()
    if models:
        for i,m in enumerate(models,1): print(f"  {i}) {m}")
        pick=input("number or type a name (Enter=keep) > ").strip()
        if pick.isdigit() and 1<=int(pick)<=len(models): d["model"]=models[int(pick)-1]
        elif pick: d["model"]=pick
        else: print("unchanged"); return
    else:
        m=input("type model name > ").strip()
        if not m: print("unchanged"); return
        d["model"]=m
    open(fp,"w").write(json.dumps(d,indent=2)); print(f"{name} model -> {d['model']}")
JUDGE_PREF=["qwen2.5:14b-instruct","qwen2.5-coder:14b","llama3.1:8b","hermes3:8b","llama3.2:3b"]
def best_model():
    have=list_models()
    for m in JUDGE_PREF:
        if m in have: return m
    return have[0] if have else None
def transcript():
    rows=[json.loads(l) for l in _rows() if l.strip()]
    return "\n".join(f'{r.get("agent","?")}: {r["content"]}' for r in rows if r.get("event") in ("send","reply") and r.get("content"))
def _ollama_chat(model,prompt):
    import urllib.request
    body={"model":model,"messages":[{"role":"user","content":prompt}],"stream":False,"options":{"temperature":0}}
    req=urllib.request.Request(OLLAMA+"/api/chat",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r: return json.loads(r.read())["message"]["content"].strip()
def judge():
    rows=[json.loads(l) for l in _rows() if l.strip()]
    if not rows: print("no events yet"); return
    s=summarize(rows); print(f"{_DIM}===== JUDGE ====={_R}")
    for ag,n in s["msgs"].items(): print(f'  {_AG.get(ag,"")}{ag:<6}{_R} turns: {n}')
    print(f'  errors: {s["errors"]}  |  {s["result"]}')
    t=transcript(); model=best_model()
    if t and model:
        print(f"\n{_DIM}--- AI judge ({model}) ---{_R}")
        rub=("Two AIs (Alice, Bob) are having an open conversation. Rate how NATURAL and engaging "
             "each one is from 1 to 5, note if they stay coherent and build on each other, and give "
             "a one-line verdict. Be concise.\n\nTRANSCRIPT:\n"+t)
        try: print(_ollama_chat(model,rub))
        except Exception as e: print(f"AI judge unavailable ({e})")
def caps_all():
    for name in ("alice","bob","carlos"):
        spec=importlib.util.spec_from_file_location("ag_"+name,LAB/"agents"/name/"agent.py")
        m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(m.caps_text())
def _setdot(d,key,val):
    if "." in key: a,b=key.split(".",1); d.setdefault(a,{})[b]=val
    else: d[key]=val
def _getdot(d,key):
    if "." in key: a,b=key.split(".",1); return (d.get(a) or {}).get(b)
    return d.get(key)
CFG_FIELDS=[("model","text"),("system","text"),("opening","text"),("anchor","bool"),
 ("auto_delay","num"),("loop.max_turns","num"),("stop.token","text"),("stop.min_turns","num"),
 ("interval","num"),("memory.enabled","bool"),("memory.keep_turns","num")]
def configure():
    name=input("agent? (alice/bob/carlos) > ").strip().lower(); fp=LAB/"agents"/name/"config.json"
    if not fp.exists(): print("no such agent"); return
    d=json.load(open(fp)); keys=[k for k,_ in CFG_FIELDS]; types=dict(CFG_FIELDS)
    while True:
        print(f"\n{_AG.get(name,'')}--- {name} config ---{_R}")
        for k,_ in CFG_FIELDS: print(f"  {k:<16}= {str(_getdot(d,k))[:60]}")
        print(f"  {_DIM}(menu 6 edits temperature/top_k/... sampling dials){_R}")
        k=input("field (Enter=save&exit) > ").strip()
        if not k: break
        if k not in keys: print("unknown field"); continue
        raw=input(f"new value for {k} > ").strip(); t=types[k]
        if t=="bool": val=raw.lower() in ("1","true","yes","on","y")
        elif t=="num":
            try: f=float(raw); val=int(f) if f.is_integer() else f
            except ValueError: print("must be a number"); continue
        else: val=raw
        _setdot(d,k,val); print(f"{k} = {val}")
    open(fp,"w").write(json.dumps(d,indent=2)); print(f"saved -> {name}")

def graph_view():
    gp=LAB/"logs"/"graph.json"
    if not gp.exists(): print("no graph yet - run Carlos -> report (menu 7)"); return
    g=json.loads(gp.read_text())
    print(f'{_DIM}nodes={len(g.get("nodes",[]))}  edges={len(g.get("edges",[]))}{_R}')
    for e in g.get("edges",[])[:40]:
        print(f'  {e["s"]} {_EV.get("direct","")}{e["rel"]}{_R} {e["o"]}')
    print(f'{_DIM}picture: logs/graph.md (open it to see the diagram){_R}')

def errors_view():
    if not ERR.exists() or ERR.stat().st_size==0: print("no errors logged - clean!"); return
    for l in ERR.read_text().splitlines()[-15:]:
        try:
            r=json.loads(l); print(f'{_EV.get("error","")}{r.get("ts")} {r.get("agent")} [{r.get("where")}] {r.get("error")}{_R}')
            if r.get("trace"): print(f'{_DIM}{r["trace"][-300:]}{_R}')
        except Exception: pass

def lab_version():
    try: return (LAB/"VERSION").read_text().strip()
    except Exception: return "unversioned"
def menu():
    while True:
        print(f"""
{_AG['alice']}========== AI CHAT - LAB CONTROL =========={_R}\n{_DIM}version: {lab_version()}{_R}
  1) monitor     show the conversation (colour)
  2) monitor -f  follow live
  3) reset       archive logs and start clean
  4) judge       summary + AI rating of how natural the chat was
  5) caps        both agents' capabilities
  6) params      edit an agent's LLM parameters
  7) model       change an agent's model
  8) control     pause / continue / stop / inject into a LIVE chat
  9) configure   edit ANY field of an agent (role, model, anchor, limits, memory)
 10) errors      show recent errors + tracebacks (debug)
  0) quit        (or type q)""")
        ch=input("choose > ").strip().lower()
        if ch=="1": view(False)
        elif ch=="2": view(True)
        elif ch=="3": reset()
        elif ch=="4": judge()
        elif ch=="5": caps_all()
        elif ch=="6": edit_params()
        elif ch=="7": set_model()
        elif ch=="8": director()
        elif ch=="9": configure()
        elif ch=="10": errors_view()
        elif ch=="11": graph_view()
        elif ch in ("0","q","quit","exit"): break
        else: print("pick a number")
if __name__=="__main__":
    a=sys.argv[1:]
    try:
        if not a: menu()
        elif a[0]=="monitor": view("-f" in a)
        elif a[0]=="reset": reset()
        elif a[0]=="judge": judge()
        elif a[0]=="caps": caps_all()
        else: print(__doc__)
    except KeyboardInterrupt: print("\nbye")
