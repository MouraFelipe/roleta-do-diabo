"""Testa as regras, o modo contra bots, o passa e joga e a sala online (3 navegadores).
Online usa um servidor PeerJS local: precisa de `npx peerjs --port 9000` (pacote `peer`) rodando.
Uso: python tests/test_jogo.py [pasta do pacote peerjs para servir o script offline]"""
import os, subprocess, sys, time
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PEERJS = sys.argv[1] if len(sys.argv) > 1 else None
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8810", "--directory", ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
URL = "http://localhost:8810/index.html"
errors = []
def page(ctx):
    p = ctx.new_page(); p.on("pageerror", lambda e: errors.append(str(e)))
    if PEERJS: p.route("**/peerjs.min.js", lambda r: r.fulfill(path=PEERJS, content_type="application/javascript"))
    p.route("**/fonts.googleapis.com/**", lambda r: r.abort()); return p
try:
  with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
    p = page(ctx); p.goto(URL); p.wait_for_selector("#bots")
    # regras puras
    r = p.evaluate("""()=>{ const G=newGame([{id:'a',name:'A'},{id:'b',name:'B'},{id:'c',name:'C'}]); G.turn=0; G.pos=2; G.bullet=3;
      const out={};
      out.notTurn = act(G,1,{t:'shoot'}).err;
      act(G,0,{t:'peekPub'}); out.pub=G.pub[2]; out.coins=G.players[0].coins;
      const s=act(G,0,{t:'peekSec',c:1}); out.priv=s.priv; out.secretOnlyA = G.players[0].know[3]==='B' && !G.players[1].know[3] && !G.pub[3];
      out.v = JSON.stringify(viewFor(G,1)).includes('bullet');
      act(G,0,{t:'shoot'}); out.after={pos:G.pos, coins:G.players[0].coins, turn:G.turn};
      act(G,1,{t:'spin',n:-1}); out.back=G.pos; out.c1=G.players[1].coins;
      out.broke = act(G,1,{t:'spin',n:-2}).err;
      act(G,1,{t:'spin',n:2}); out.fwd=G.pos;           // 5
      act(G,1,{t:'spin',n:-2});                          // 3 = bala
      return out; }""")
    print("regras:", r)
    assert r["notTurn"] and r["pub"] == "V" and r["coins"] == 4 and "TEM BALA" in r["priv"] and r["secretOnlyA"] and not r["v"]
    assert r["after"] == {"pos": 3, "coins": 2, "turn": 1} and r["back"] == 2 and r["c1"] == 1 and r["broke"]
    bang = p.evaluate("""()=>{ const G=newGame([{id:'a',name:'A'},{id:'b',name:'B'},{id:'c',name:'C'}]); G.turn=0; G.pos=1; G.bullet=1;
       act(G,0,{t:'shoot'}); const r1={alive:G.players[0].alive, turn:G.turn, round:G.round, pub:Object.keys(G.pub).length};
       G.pos=G.bullet; act(G,G.turn,{t:'shoot'}); return {r1, over:G.over, winner:G.winner}; }""")
    print("eliminação:", bang); assert bang["r1"] == {"alive": False, "turn": 1, "round": 2, "pub": 0} and bang["over"] and bang["winner"] == 2
    # contra bots até o fim
    p.click("#bots"); p.fill("#nm", "Felipe"); p.click("#go"); p.wait_for_selector(".stage")
    p.screenshot(path="/tmp/rd_jogo.png")
    for _ in range(1500):
        if p.query_selector("#again"): break
        if p.query_selector("#shoot:not([disabled])"):
            if p.query_selector('[data-a="peekSec"]:not([disabled])') and not p.query_selector(".pick"):
                p.click('[data-a="peekSec"]'); p.click('[data-o="0"]'); p.wait_for_timeout(200); p.screenshot(path="/tmp/rd_secreto.png")
            p.click("#shoot")
        p.wait_for_timeout(250)
    assert p.query_selector("#again"); print("contra bots:", p.inner_text(".status").replace("\n", " ")); p.screenshot(path="/tmp/rd_fim.png")
    # passa e joga
    p.click("#exit"); p.click("#local"); p.wait_for_selector(".pn")
    for i, n in enumerate(["Ana", "Bia", "Caio"]): p.locator(".pn").nth(i).fill(n)
    p.click("#go"); p.wait_for_selector("#rv"); p.screenshot(path="/tmp/rd_passa.png"); who = p.inner_text("h1"); p.click("#rv"); p.wait_for_selector("#shoot")
    p.click("#shoot"); assert p.query_selector("#rv") or p.query_selector("#again"); print("passa e joga: primeiro foi", who)
    p.close()
    # online: 3 navegadores
    if PEERJS:
        q = "?peerhost=localhost&peerport=9000"
        h = page(b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")); h.goto(URL.replace("index.html", "index.html" + q))
        h.click("#host"); h.fill("#nm", "Felipe"); h.click("#go"); h.wait_for_selector(".code", timeout=15000); code = h.inner_text(".code"); print("sala:", code)
        gs = []
        for n in ["Ana", "Bia"]:
            g = page(b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")); g.goto(URL + q + "#sala-" + code)
            g.click("#joinHash"); g.fill("#nm", n); g.click("#go"); g.wait_for_selector("text=Esperando", timeout=15000); gs.append(g)
        h.wait_for_selector("#start:not([disabled])"); h.screenshot(path="/tmp/rd_sala.png"); h.click("#start")
        for g in gs: g.wait_for_selector(".stage")
        all_p = [h] + gs; secret_seen = False
        for _ in range(300):
            if h.query_selector("#again"): break
            for x in all_p:
                if x.query_selector("#shoot:not([disabled])"):
                    if not secret_seen and x.query_selector('[data-a="peekSec"]:not([disabled])'):
                        x.click('[data-a="peekSec"]'); x.click('[data-o="0"]'); x.wait_for_selector(".toast"); t = x.inner_text(".toast")
                        others = [o for o in all_p if o is not x]; secret_seen = True
                        print("segredo:", t, "| outros veem marca secreta?", any(o.query_selector('circle[stroke-dasharray]') for o in others))
                        assert not any(o.query_selector('circle[stroke-dasharray]') for o in others)
                    x.click("#shoot"); x.wait_for_timeout(300)
            h.wait_for_timeout(150)
        for x in all_p: x.wait_for_selector("#again", timeout=10000)
        print("online:", [x.inner_text(".win") for x in all_p])
    b.close()
  print("erros:", errors); assert not errors
finally:
    srv.terminate()
