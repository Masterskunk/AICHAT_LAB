#!/usr/bin/env python3
"""Reflective IDEATOR engine (Aradia=Mac local; Danaris=Windows remote-file; Colossus=Pi MCP/chat).
Reads a knowledge graph from one of several SOURCES (config-driven) and proposes NEW concepts to
enhance the lab (appends its outfile). No chat, no inbound HTTP. Graph sources:
  local (default)        - read logs/graph.json on this machine (Aradia)
  graph_url              - HTTP GET a graph.json over the LAN (Danaris)
  mcp_url + request_via=mcp  - JSON-RPC tools/call 'full_graph' to an MCP endpoint (Colossus)
  chat_peer + request_via=chat - POST a GRAPH_REQUEST and get the graph back 'via chat' (Colossus)
No args = MENU."""
import json, sys, time, platform, urllib.request, importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent; CFG=HERE/"config.json"
LOGS=HERE.parent.parent/"logs"; EVENTS=LOGS/"events.jsonl"; ERR=LOGS/"errors.jsonl"
MODDIR=HERE.parent.parent/"modules"
_R="\033[0m"; _DIM="\033[2m"; _REDC="\033[1;91m"; _OK="\033[1;92m"
def cfg(): return json.loads(CFG.read_text())
try: GOLD=cfg().get("color") or "\033[1;38;5;220m"
except Exception: GOLD="\033[1;38;5;220m"

def log(event,**kw):
    LOGS.mkdir(parents=True,exist_ok=True)
    rec={"ts":time.strftime("%H:%M:%S"),"agent":cfg().get("name","aradia"),"event":event,**kw}
    EVENTS.open("a").write(json.dumps(rec)+"\n")
def logerr(where,e):
    import traceback
    LOGS.mkdir(parents=True,exist_ok=True)
    rec={"ts":time.strftime("%H:%M:%S"),"agent":cfg().get("name","aradia"),"where":where,"error":str(e),"trace":traceback.format_exc()[-1000:]}
    ERR.open("a").write(json.dumps(rec)+"\n"); print(f"{_REDC}[ERROR {where}] {e}{_R}")

# ---- pure helpers (offline-testable) ----
def parse_tags(data):
    return [m.get("name","") for m in (data or {}).get("models",[]) if m.get("name")]
def pick_model(choice, names, current):
    choice=(choice or "").strip()
    if not choice: return current
    if choice.isdigit():
        i=int(choice)-1
        return names[i] if 0<=i<len(names) else current
    return choice
def coerce(kind, raw, current):
    raw=(raw or "").strip()
    if raw=="": return current
    try:
        if kind=="int": return int(raw)
        if kind=="float": return float(raw)
        if kind=="bool": return raw.lower() in ("1","true","on","yes","y")
    except Exception: return current
    return raw

# ---- graph sources ----
def _http_json(url, data=None, timeout=20):
    hdr={"Content-Type":"application/json"} if data is not None else {}
    req=urllib.request.Request(url,data=(json.dumps(data).encode() if data is not None else None),headers=hdr)
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.loads(r.read())
def mcp_fetch_graph(url):
    """MCP: JSON-RPC 2.0 tools/call 'full_graph'. Result text is the graph JSON."""
    try:
        resp=_http_json(url,{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"full_graph","arguments":{}}})
        return json.loads(resp["result"]["content"][0]["text"])
    except Exception as e:
        print(f"{_REDC}MCP request failed to {url}: {e}{_R}"); return {"nodes":[],"edges":[]}
def chat_fetch_graph(url):
    """'Via chat': POST a GRAPH_REQUEST, peer replies with the graph."""
    try:
        resp=_http_json(url,{"from":cfg().get("name","colossus"),"content":"GRAPH_REQUEST"})
        return resp.get("graph") or {"nodes":[],"edges":[]}
    except Exception as e:
        print(f"{_REDC}chat request failed to {url}: {e}{_R}"); return {"nodes":[],"edges":[]}
def read_graph():
    c=cfg(); via=c.get("request_via")
    if (via=="mcp" or (not via and c.get("mcp_url"))) and c.get("mcp_url"): return mcp_fetch_graph(c["mcp_url"])
    if (via=="chat" or (not via and c.get("chat_peer"))) and c.get("chat_peer"): return chat_fetch_graph(c["chat_peer"])
    if c.get("graph_url"):
        try: return _http_json(c["graph_url"])
        except Exception as e: print(f"{_REDC}could not fetch {c['graph_url']}: {e}{_R}"); return {"nodes":[],"edges":[]}
    try: return json.loads((LOGS/"graph.json").read_text())
    except Exception: return {"nodes":[],"edges":[]}
def graph_source():
    c=cfg(); via=c.get("request_via")
    if (via=="mcp" or not via) and c.get("mcp_url"): return f"MCP {c['mcp_url']}"
    if (via=="chat" or not via) and c.get("chat_peer"): return f"chat {c['chat_peer']}"
    if c.get("graph_url"): return c["graph_url"]
    return "logs/graph.json (local)"

# ---- model IO ----
def load_ideator():
    spec=importlib.util.spec_from_file_location("ideator",MODDIR/"ideator.py")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def ollama_tags():
    return parse_tags(_http_json(cfg()["ollama"]+"/api/tags"))
def chat(system,user):
    c=cfg(); body={"model":c["model"],"messages":[{"role":"system","content":system},{"role":"user","content":user}],
                   "stream":False,"options":c.get("options",{}),"keep_alive":c.get("keep_alive","5m")}
    if "think" in c: body["think"]=bool(c["think"])
    req=urllib.request.Request(c["ollama"]+"/api/chat",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=300) as r: return json.loads(r.read())["message"]["content"].strip()

# ---- menu actions ----
def caps():
    c=cfg(); ic=c.get("ideator",{}); o=c.get("options",{})
    print(f'{GOLD}agent={c["name"]} role=ideator model={c["model"]} think={c.get("think","-")} '
          f'platform={platform.system()}/{platform.machine()} graph={graph_source()} '
          f'writes=logs/{ic.get("outfile","aradia_ideas.md")} n={ic.get("n",8)} '
          f'temp={o.get("temperature","-")} num_ctx={o.get("num_ctx","-")}{_R}')
def ideate():
    c=cfg(); g=read_graph()
    if not g.get("edges"):
        print(f"{GOLD}no graph facts from {graph_source()} - is the source populated / reachable?{_R}"); return
    ic=c.get("ideator",{}); n=int(ic.get("n",8)); outfile=LOGS/ic.get("outfile","aradia_ideas.md")
    print(f"{_DIM}read {len(g['edges'])} facts from {graph_source()}, asking {c['model']} for {n} new concepts...{_R}")
    try:
        mod=load_ideator(); concepts,entry=mod.ideate(g, chat, model=c["model"], n=n)
    except Exception as e:
        logerr("ideate",e); return
    outfile.parent.mkdir(parents=True,exist_ok=True)
    with outfile.open("a") as f: f.write(entry)
    log("ideate",concepts=len(concepts),model=c["model"],source=graph_source())
    print(f"{GOLD}{entry}{_R}{_DIM}appended {len(concepts)} concepts -> logs/{outfile.name}{_R}")
def model():
    c=cfg(); print(f"{GOLD}current model: {c['model']}{_R}")
    try: names=ollama_tags()
    except Exception as e:
        print(f"{_REDC}could not reach Ollama ({e}). Type a model name manually.{_R}"); names=[]
    for i,nm in enumerate(names,1):
        print(f"  {GOLD}{i}{_R}) {nm}{_OK}{' <= current' if nm==c['model'] else ''}{_R}")
    newm=pick_model(input("pick number or type a model name (blank=keep) > "),names,c["model"])
    if newm!=c["model"]: c["model"]=newm; CFG.write_text(json.dumps(c,indent=2)); print(f"{_OK}model -> {newm}{_R}")
    else: print(f"{_DIM}kept {c['model']}{_R}")
def params():
    c=cfg(); ic=c.setdefault("ideator",{}); o=c.setdefault("options",{})
    print(f"{GOLD}params (blank = keep){_R}")
    ic["n"]=coerce("int",input(f"  ideas per run n [{ic.get('n',8)}] > "),ic.get("n",8))
    o["temperature"]=coerce("float",input(f"  temperature [{o.get('temperature',0.8)}] > "),o.get("temperature",0.8))
    o["num_ctx"]=coerce("int",input(f"  num_ctx [{o.get('num_ctx',16384)}] > "),o.get("num_ctx",16384))
    cur=c.get("think",None)
    t=input(f"  thinking on/off [{cur if cur is not None else 'unset'}] (blank=keep, 'none'=remove) > ").strip().lower()
    if t=="none": c.pop("think",None)
    elif t!="": c["think"]=t in ("1","true","on","yes","y")
    CFG.write_text(json.dumps(c,indent=2)); print(f"{_OK}saved: n={ic['n']} temp={o['temperature']} num_ctx={o['num_ctx']} think={c.get('think','unset')}{_R}")
def source_menu():
    c=cfg(); print(f"{GOLD}graph source now: {graph_source()}{_R}")
    opts=[]
    if c.get("mcp_url"): opts.append(("mcp",f"MCP  {c['mcp_url']}"))
    if c.get("chat_peer"): opts.append(("chat",f"chat {c['chat_peer']}"))
    if c.get("graph_url"): opts.append(("file",f"file {c['graph_url']}"))
    opts.append(("local","local logs/graph.json"))
    for i,(k,d) in enumerate(opts,1): print(f"  {GOLD}{i}{_R}) {d}")
    ch=input("pick number (blank=keep) > ").strip()
    if ch.isdigit() and 1<=int(ch)<=len(opts):
        k=opts[int(ch)-1][0]
        if k=="local": c.pop("request_via",None); c.pop("graph_url",None)  # note: clears file too
        else: c["request_via"]=k
        CFG.write_text(json.dumps(c,indent=2)); print(f"{_OK}source -> {graph_source()}{_R}")
def view():
    c=cfg(); f=LOGS/c.get("ideator",{}).get("outfile","aradia_ideas.md")
    if not f.exists(): print(f"{_DIM}no ideas yet ({f.name}){_R}"); return
    print(f"{GOLD}--- last of logs/{f.name} ---{_R}\n"+"\n".join(f.read_text().strip().splitlines()[-40:]))

def menu():
    while True:
        c=cfg()
        print(f"""
{GOLD}========== {c['name'].upper()}  (reflective ideator) =========={_R}
  {GOLD}1{_R}) caps      what I am / model / graph source
  {GOLD}2{_R}) ideate    request the graph, propose NEW concepts to enhance the lab
  {GOLD}3{_R}) model     choose which Ollama model I use
  {GOLD}4{_R}) params    ideas-per-run, temperature, num_ctx, thinking on/off
  {GOLD}5{_R}) source    where I get the graph (local / file / MCP / chat)
  {GOLD}6{_R}) view      show my latest ideas
  {GOLD}0{_R}) quit      (or type q)
{_DIM}model={c['model']}  graph={graph_source()}  |  Ctrl-C aborts a run.{_R}""")
        ch=input("choose > ").strip().lower()
        try:
            if ch=="1": caps()
            elif ch=="2": ideate()
            elif ch=="3": model()
            elif ch=="4": params()
            elif ch=="5": source_menu()
            elif ch=="6": view()
            elif ch in ("0","q","quit","exit"): break
            else: print("pick a number")
        except Exception as e: logerr("menu",e)

if __name__=="__main__":
    a=sys.argv[1:]
    try:
        if not a: menu()
        elif a[0]=="caps": caps()
        elif a[0]=="ideate": ideate()
        elif a[0]=="model": model()
        else: print(__doc__)
    except KeyboardInterrupt: print("\nbye")
