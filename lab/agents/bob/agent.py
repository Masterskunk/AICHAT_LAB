#!/usr/bin/env python3
"""AI chat agent. No args = MENU. Deploy: listen | send "msg" | direct | caps."""
import json, sys, time, traceback, urllib.request, urllib.error, importlib.util, platform
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
HERE=Path(__file__).resolve().parent; CFG_FILE=HERE/"config.json"
LOGS=HERE.parent.parent/"logs"
LOG=LOGS/"events.jsonl"; TRACE=LOGS/"trace.jsonl"; ERR=LOGS/"errors.jsonl"; CTRL=LOGS/"control.json"
def cfg(): return json.loads(CFG_FILE.read_text())
_R="\033[0m"; _DIM="\033[2m"
_AG={"alice":"\033[1;96m","bob":"\033[1;38;5;214m","carlos":"\033[1;92m"}
_EV={"send":"\033[1;93m","reply":"\033[1;93m","recv":"\033[1;94m","start":"\033[1;97m","done":"\033[1;97m","error":"\033[1;91m","direct":"\033[1;92m","inject":"\033[1;95m","paused":"\033[1;90m"}
_ARROW={"send":"▶","reply":"▶","recv":"◀"}
def _line(rec):
    ag=rec.get("agent","");ev=rec.get("event","")
    ac=_AG.get(ag,"\033[1;97m");ec=_EV.get(ev,"\033[1;97m");ar=_ARROW.get(ev,"•")
    extra=" ".join(f"{k}={v}" for k,v in rec.items() if k not in ("ts","agent","event","content"))
    head=f'{_DIM}{rec.get("ts","")}{_R} {ac}{ag.upper():<6}{_R} {ec}{ar} {ev.upper():<6}{_R} {_DIM}{extra}{_R}'
    body=f'\n    {ac}{rec["content"]}{_R}' if rec.get("content") else ""
    return head+body+("\n" if ev in ("recv","done","error") else "")
def log(event,**kw):
    LOG.parent.mkdir(parents=True,exist_ok=True)
    rec={"ts":time.strftime("%H:%M:%S"),"agent":cfg()["name"],"event":event,**kw}
    LOG.open("a").write(json.dumps(rec)+"\n"); print(_line(rec))
def logerr(where,e):
    ERR.parent.mkdir(parents=True,exist_ok=True)
    rec={"ts":time.strftime("%H:%M:%S"),"agent":cfg().get("name","?"),"where":where,"error":str(e),"trace":traceback.format_exc()[-1000:]}
    ERR.open("a").write(json.dumps(rec)+"\n")
    print(f"{_EV['error']}[ERROR {where}] {e}{_R}")
    try: log("error",where=where,err=str(e)[:120])
    except Exception: pass
_TID=[0]
def trace(step,**kw):
    if not cfg().get("trace"): return
    _TID[0]+=1
    rec={"tid":_TID[0],"ts":time.strftime("%H:%M:%S"),"agent":cfg()["name"],"step":step,**kw}
    TRACE.parent.mkdir(parents=True,exist_ok=True); TRACE.open("a").write(json.dumps(rec)+"\n")
    if cfg().get("log_level")=="debug":
        print(f'{_DIM}  trace t{rec["tid"]:<3} {step:<6} '+" ".join(f"{k}={v}" for k,v in kw.items())+_R)
def read_ctrl():
    try: return json.loads(CTRL.read_text())
    except Exception: return {"state":"run","inject":None}
def write_ctrl(d):
    CTRL.parent.mkdir(parents=True,exist_ok=True); CTRL.write_text(json.dumps(d))
def mem_path(c): return LOGS/f'mem_{c["name"]}.txt'
def mem_read(c):
    try: return mem_path(c).read_text().strip()
    except Exception: return ""
def mem_write(c,note):
    p=mem_path(c); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a") as f: f.write(note.strip()[:200]+"\n")
MODDIR=LOGS.parent/"modules"
def load_modules(c):
    mods=[]; tools={}
    for name,on in (c.get("modules") or {}).items():
        if not on: continue
        f=MODDIR/(name+".py")
        if not f.exists(): print(f"[warn] module {name} missing"); continue
        try:
            spec=importlib.util.spec_from_file_location("mod_"+name,f); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            if hasattr(m,"on_start"): m.on_start(c)
            tools.update(getattr(m,"TOOLS",{})); mods.append(name)
        except Exception as e: logerr("load_modules:"+name,e)
    return mods,tools
def chat(messages):
    c=cfg(); body={"model":c["model"],"messages":messages,"stream":False,"options":c.get("options",{}),"keep_alive":c.get("keep_alive","5m")}
    req=urllib.request.Request(c["ollama"]+"/api/chat",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r: return json.loads(r.read())["message"]["content"].strip()
ANCHOR=" Have a GROUNDED, specific conversation. Each turn make ONE concrete point or ask ONE specific question and build on what the other said. Do NOT narrate the conversation, announce endings, or use grandiose, cosmic or ALL-CAPS language. Talk plainly."
def build_system(c):
    s=c["system"].replace("{secret}",str(c.get("secret","")))
    return s+ANCHOR if c.get("anchor") else s
def build_messages(c,history):
    msgs=[{"role":"system","content":build_system(c)}]; mem=c.get("memory") or {}
    if mem.get("enabled"):
        notes=mem_read(c)
        if notes: msgs.append({"role":"system","content":"Your memory of the conversation so far (rely on this instead of re-reading everything):\n"+notes})
        keep=int(mem.get("keep_turns",3))*2
        msgs+= history[-keep:] if keep>0 else []
    else:
        msgs+=history
    return msgs
def think(history):
    c=cfg(); msgs=build_messages(c,history)
    t0=time.time(); reply=chat(msgs); ms=int((time.time()-t0)*1000)
    trace("think",msgs=len(msgs),mem=1 if (c.get("memory") or {}).get("enabled") else 0,ms=ms,reply=reply[:80])
    return reply
def clean(reply): return "" if reply is None else " ".join(reply.split()).strip()
def referee(incoming,c):
    sec=c.get("secret")
    if sec and sec.lower() in (incoming or "").lower(): return f"CORRECT, it is {sec}."
    return None
def respond(content,hist):
    c=cfg(); hist.append({"role":"user","content":content})
    try:
        win=referee(content,c); reply=win if win is not None else clean(think(hist))
    except Exception as e:
        logerr("respond",e); reply="(error generating reply - see logs/errors.jsonl)"
    hist.append({"role":"assistant","content":reply})
    if (c.get("memory") or {}).get("enabled"): mem_write(c,"said: "+reply)
    return reply
def is_done(text,c):
    tok=(c.get("stop") or {}).get("token"); return bool(tok) and tok.upper() in (text or "").upper()
def post(url,obj):
    req=urllib.request.Request(url,data=json.dumps(obj).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r: return json.loads(r.read())
def listen():
    c=cfg(); hist=[]
    class H(BaseHTTPRequestHandler):
        def log_message(self,*a): pass
        def do_POST(self):
            try:
                n=int(self.headers.get("Content-Length",0)); msg=json.loads(self.rfile.read(n))
                log("recv",frm=msg.get("from","?"),content=msg["content"])
                reply=respond(msg["content"],hist); log("reply",content=reply)
                out=json.dumps({"from":c["name"],"content":reply}).encode()
            except Exception as e:
                logerr("listen",e); out=json.dumps({"from":c["name"],"content":"(error)"}).encode()
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(out)
    log("start",mode="listen",port=c["port"],model=c["model"]); HTTPServer((c["host"],c["port"]),H).serve_forever()
def send(first):
    c=cfg(); hist=[]; maxt=(c.get("loop") or {}).get("max_turns",c.get("max_turns",4))
    mint=(c.get("stop") or {}).get("min_turns",1); delay=c.get("auto_delay",0)
    log("start",mode="send",peer=c["peer_url"],model=c["model"])
    for turn in range(1,maxt+1):
        try:
            paused=False
            while read_ctrl().get("state")=="pause":
                if not paused: log("paused",turn=turn); paused=True
                time.sleep(1)
            ctl=read_ctrl()
            if ctl.get("state")=="stop":
                log("finished",reason="control_stop",turns=turn-1); write_ctrl({"state":"run","inject":None}); return
            inj=ctl.get("inject")
            if turn==1: text=first
            elif inj: text=clean(inj); write_ctrl({**ctl,"inject":None}); log("inject",turn=turn,content=text)
            else: text=clean(think(hist))
            hist.append({"role":"assistant","content":text}); log("send",turn=turn,content=text)
            if (c.get("memory") or {}).get("enabled") and turn>1 and not inj: mem_write(c,"said: "+text)
            r=post(c["peer_url"]+"/message",{"from":c["name"],"content":text})
            log("recv",turn=turn,content=r["content"]); hist.append({"role":"user","content":r["content"]})
            if turn>=mint and (is_done(text,c) or is_done(r["content"],c)):
                trace("stop",turn=turn); log("finished",reason="done",turns=turn); return
            if delay: time.sleep(delay)
        except (urllib.error.URLError,OSError) as e:
            logerr("send.net",e); return
        except Exception as e:
            logerr("send",e); return
    log("done",reason="max_turns",turns=maxt)
def lab_version():
    try: return (LOGS.parent/"VERSION").read_text().strip()
    except Exception: return "unversioned"
def caps_text():
    c=cfg(); mods,tools=load_modules(c)
    return (f'agent={c["name"]} model={c["model"]} platform={platform.system()}/{platform.machine()} '
            f'python={platform.python_version()} version="{lab_version()}" memory={"on" if (c.get("memory") or {}).get("enabled") else "off"} '
            f'modules=[{",".join(mods) or "none"}] tools=[{",".join(sorted(tools)) or "none"}]')
def caps(): print(caps_text())
def send_once(text):
    c=cfg(); log("send",turn=1,content=text)
    try: r=post(c["peer_url"]+"/message",{"from":c["name"],"content":text})
    except Exception as e: logerr("send_once",e); return None
    log("recv",turn=1,content=r["content"]); return r["content"]
def send_caps(): return send_once("Here are my capabilities -> "+caps_text())
def decide(text):
    t=(text or "").strip(); up=t.upper()
    if up.startswith("STOP"): return ("stop",None)
    if up.startswith("PAUSE"): return ("pause",None)
    if up.startswith("INJECT"): return ("inject",t[6:].lstrip(": ").strip() or None)
    return ("continue",None)
def direct():
    c=cfg(); interval=c.get("interval",20); need=c.get("min_before_act",4); seen=0
    log("start",mode="direct",model=c["model"])
    while True:
        try:
            if read_ctrl().get("state")=="stop": log("finished",reason="stopped"); return
            rows=[json.loads(l) for l in (LOG.read_text().splitlines() if LOG.exists() else []) if l.strip()]
            convo=[f'{r["agent"]}: {r["content"]}' for r in rows if r.get("event") in ("send","reply") and r.get("content")]
            if len(convo)>seen and len(convo)>=need:
                seen=len(convo)
                out=chat([{"role":"system","content":build_system(c)},
                          {"role":"user","content":"CONVERSATION:\n"+"\n".join(convo[-20:])+"\n\nYour decision (CONTINUE | PAUSE | STOP | INJECT: <line>):"}])
                action,line=decide(out); log("direct",action=action,content=(line or ""))
                if action=="stop": write_ctrl({"state":"stop","inject":None}); log("finished",reason="carlos_stop"); return
                elif action=="pause": write_ctrl({**read_ctrl(),"state":"pause"})
                elif action=="inject" and line: write_ctrl({**read_ctrl(),"inject":line})
                elif action=="continue":
                    cur=read_ctrl()
                    if cur.get("state")=="pause": write_ctrl({**cur,"state":"run"})
        except Exception as e:
            logerr("direct",e)
        time.sleep(interval)
def report():
    """Carlos: read the whole chat, extract triples, update the knowledge graph, render it."""
    c=cfg()
    spec=importlib.util.spec_from_file_location("mg",MODDIR/"memory_graph.py")
    mg=importlib.util.module_from_spec(spec); spec.loader.exec_module(mg)
    rows=[json.loads(l) for l in (LOG.read_text().splitlines() if LOG.exists() else []) if l.strip()]
    convo="\n".join(f'{r["agent"]}: {r["content"]}' for r in rows if r.get("event") in ("send","reply") and r.get("content"))
    if not convo: print("no conversation yet"); return
    log("start",mode="report",model=c["model"])
    try:
        out=chat([{"role":"system","content":"You extract knowledge from a conversation as TRIPLES. "
                   "Output ONLY lines in the form: subject | relation | object . Use short lowercase concepts, no extra text."},
                  {"role":"user","content":"CONVERSATION:\n"+convo[-6000:]+"\n\nTriples:"}])
    except Exception as e: logerr("report",e); return
    gpath=str(LOGS/"graph.json"); triples=mg.parse_triples(out)
    added,nn,ne=mg.add_triples(triples,gpath); mg.render_mermaid(gpath,str(LOGS/"graph.md"))
    log("report",triples=len(triples),added=added,nodes=nn,edges=ne)
    print(f"graph: +{added} new, now {nn} nodes / {ne} edges -> logs/graph.json , picture in logs/graph.md")

def menu():
    while True:
        c=cfg(); ac=_AG.get(c["name"],"\033[1;97m")
        print(f"""
{ac}========== AI CHAT : {c["name"].upper()} =========={_R}
  {ac}1{_R}) caps       what I am / where I run / my tools
  {ac}2{_R}) listen     wait for messages and reply
  {ac}3{_R}) talk       start a conversation (type the opening topic)
  {ac}4{_R}) introduce  send MY caps to my peer
  {ac}5{_R}) message    send one typed message
  {ac}6{_R}) direct     watch & steer the chat (Carlos)
  {ac}7{_R}) report     build the knowledge graph from the chat (Carlos)
  {ac}0{_R}) quit       (or type q)
{_DIM}Stop a running loop with Ctrl-C.{_R}""")
        ch=input("choose > ").strip().lower()
        try:
            if ch=="1": caps()
            elif ch=="2":
                print(f"{_DIM}listening... Ctrl-C to stop{_R}")
                try: listen()
                except KeyboardInterrupt: print("stopped")
            elif ch=="3":
                m=input("opening topic > ").strip() or cfg().get("opening","Hello.")
                try: send(m)
                except KeyboardInterrupt: print("\nstopped")
            elif ch=="4": send_caps()
            elif ch=="5":
                m=input("message > ").strip()
                if m: send_once(m)
            elif ch=="6":
                print(f"{_DIM}directing... Ctrl-C to stop{_R}")
                try: direct()
                except KeyboardInterrupt: print("stopped")
            elif ch=="7": report()
            elif ch in ("0","q","quit","exit"): break
            else: print("pick a number")
        except Exception as e: logerr("menu",e)
if __name__=="__main__":
    a=sys.argv[1:]
    try:
        if not a: menu()
        elif a[0]=="listen": listen()
        elif len(a)>=2 and a[0]=="send": send(" ".join(a[1:]))
        elif a[0]=="direct": direct()
        elif a[0]=="report": report()
        elif a[0]=="caps": caps()
        else: print(__doc__)
    except KeyboardInterrupt: print("\nbye")
