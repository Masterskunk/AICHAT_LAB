#!/usr/bin/env python3
"""Publish the shared knowledge graph over the LAN for remote ideator agents.
Three doors onto logs/graph.json:
  GET  /graph.json , /graph.md     - plain file (Danaris reads this)
  POST /mcp                        - MCP JSON-RPC 2.0: tools/list, tools/call {full_graph|recall|query}
  POST /ask  {"content":"GRAPH_REQUEST"} -> {"graph": {...}}  ('via chat' request; Colossus)
Binds 0.0.0.0 so the LAN can reach it.  Usage: python3 tools/graph_server.py [port]"""
import sys, json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
LOGS=Path(__file__).resolve().parent.parent/"logs"
PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8800

def load_graph():
    try: return json.loads((LOGS/"graph.json").read_text())
    except Exception: return {"nodes":[],"edges":[]}
def edges_text(g, k=200):
    return "\n".join(f'{e.get("s","")} {e.get("rel","")} {e.get("o","")}' for e in g.get("edges",[])[:k])
def query_text(g, topic):
    t=(topic or "").lower()
    hits=[e for e in g.get("edges",[]) if t in (e.get("s","")+e.get("rel","")+e.get("o","")).lower()]
    return "\n".join(f'{e["s"]} {e["rel"]} {e["o"]}' for e in hits) or "(no matching facts)"

TOOLS=[
  {"name":"full_graph","description":"Return the entire knowledge graph as JSON.","inputSchema":{"type":"object","properties":{}}},
  {"name":"recall","description":"Return the first k facts as text.","inputSchema":{"type":"object","properties":{"k":{"type":"integer"}}}},
  {"name":"query","description":"Return facts whose text contains a topic.","inputSchema":{"type":"object","properties":{"topic":{"type":"string"}}}},
]
def mcp_handle(req):
    mid=req.get("id"); method=req.get("method"); p=req.get("params") or {}
    if method=="tools/list":
        return {"jsonrpc":"2.0","id":mid,"result":{"tools":TOOLS}}
    if method=="tools/call":
        name=p.get("name"); args=p.get("arguments") or {}; g=load_graph()
        if name=="full_graph": text=json.dumps(g)
        elif name=="recall": text=edges_text(g,int(args.get("k",200)))
        elif name=="query": text=query_text(g,args.get("topic",""))
        else: return {"jsonrpc":"2.0","id":mid,"error":{"code":-32602,"message":f"unknown tool {name}"}}
        return {"jsonrpc":"2.0","id":mid,"result":{"content":[{"type":"text","text":text}]}}
    return {"jsonrpc":"2.0","id":mid,"error":{"code":-32601,"message":f"unknown method {method}"}}

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _send(self,obj,ctype="application/json",code=200,raw=None):
        data=raw if raw is not None else json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        p=self.path.split("?")[0]
        f={"/graph.json":LOGS/"graph.json","/graph.md":LOGS/"graph.md","/":LOGS/"graph.json"}.get(p)
        if not f or not f.exists(): self._send(None,"text/plain",404,b"not found"); return
        self._send(None,("application/json" if f.suffix==".json" else "text/plain; charset=utf-8"),200,f.read_bytes())
    def do_POST(self):
        p=self.path.split("?")[0]
        try:
            n=int(self.headers.get("Content-Length",0)); body=json.loads(self.rfile.read(n) or b"{}")
        except Exception: self._send({"error":"bad json"},code=400); return
        if p=="/mcp": self._send(mcp_handle(body)); return
        if p=="/ask":
            if (body.get("content","")).strip().upper().startswith("GRAPH_REQUEST"):
                self._send({"from":"mac","graph":load_graph()}); return
            self._send({"from":"mac","content":edges_text(load_graph())}); return
        self._send(None,"text/plain",404,b"not found")

if __name__=="__main__":
    print(f"serving graph on 0.0.0.0:{PORT}  (GET /graph.json,/graph.md ; POST /mcp ; POST /ask)  Ctrl-C to stop")
    try: HTTPServer(("0.0.0.0",PORT),H).serve_forever()
    except KeyboardInterrupt: print("\nstopped")
