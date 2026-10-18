"""Demo module (proves the loader). Enable with config.modules.hello=true"""
def on_start(cfg): pass
def _ping(args,cfg): return "pong"
TOOLS={"ping":_ping}
