"""Testa as regras, o treino contra bots e a sala online (3 navegadores).
Online usa um servidor PeerJS local na porta 9000 (pacote `peer`).
Uso: python tests/test_jogo.py [caminho do peerjs.min.js para servir sem internet]"""
import os, subprocess, sys, time
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PEERJS = sys.argv[1] if len(sys.argv) > 1 else None
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8810", "--directory", ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
URL = "http://localhost:8810/index.html"
errors = []
def page(b):
    p = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block").new_page(); p.on("pageerror", lambda e: errors.append(str(e)))
    if PEERJS: p.route("**/peerjs.min.js", lambda r: r.fulfill(path=PEERJS, content_type="application/javascript"))
    p.route("**/fonts.googleapis.com/**", lambda r: r.abort()); return p
def play_turn(x):
    """faz 1 ação barata e passa"""
    if x.query_selector('[data-a="peekPub"]:not([disabled])'):
        x.click('[data-a="peekPub"]'); x.click('[data-s="0"]')
    else: x.click('[data-a="s1"]')
    x.wait_for_selector("#pass:not([disabled]), #again"); 
    if x.query_selector("#pass"): x.click("#pass")
try:
  with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = page(b); p.goto(URL); p.wait_for_selector("#host")
    r = p.evaluate("""()=>{ const L=n=>[...Array(n)].map((_,i)=>({id:'p'+i,name:'P'+i}));
      const o={}; o.b3=bulletsLeft(newGame(L(3))); o.b4=bulletsLeft(newGame(L(4))); o.b5=bulletsLeft(newGame(L(5))); o.b6=bulletsLeft(newGame(L(6)));
      const G=newGame(L(3),{heatSec:300}); G.seats=[0,1,2]; G.cyl=[{id:0,b:false},{id:1,b:true},{id:2,b:false}]; G.turn=0; G.players.forEach(p=>p.coins=20); G.acted=false;
      o.passFirst=act(G,0,{t:'pass'}).err; o.notTurn=act(G,1,{t:'peekPub',s:0}).err;
      act(G,0,{t:'peekPub',s:1}); o.pub=G.pub[1]; o.c0=G.players[0].coins;
      const s=act(G,0,{t:'peekSec',s:2}); o.priv=s.priv; o.secret=G.players[0].know[2]==='V' && !G.players[1].know[2];
      o.hidden=!JSON.stringify(viewFor(G,1)).includes('"b"');
      act(G,0,{t:'spin',n:1}); o.afterSpin=G.cyl.map(c=>c.id).join(); // a câmara 1 (bala) foi para o lugar 2
      act(G,0,{t:'pass'}); o.cold={turn:G.turn, alive:G.players.filter(p=>p.alive).length, c1:G.players[1].coins};
      G.start-=6*6e4; act(G,1,{t:'spin',n:-1}); o.heated=G.heated;            // bala volta para o lugar 1 (jogador 1)
      act(G,1,{t:'pass'}); o.dead=!G.players[1].alive; o.seats=G.seats.join(); o.turn=G.turn; o.reloaded=bulletsLeft(G); o.over=G.over;
      const H=newGame(L(3)); H.turn=0; H.players.forEach(p=>p.coins=20); H.pub[0]='V'; H.players[0].know[1]='B'; H.players[1].know[2]='V';
      act(H,0,{t:'hide'}); o.hide={pub:Object.keys(H.pub).length, mine:JSON.stringify(H.players[0].know), other:Object.keys(H.players[1].know).length, coins:H.players[0].coins};
      return o; }""")
    print("regras:", r); assert r["hide"] == {"pub": 0, "mine": '{"0":"V","1":"B"}', "other": 0, "coins": 14}
    assert (r["b3"], r["b4"], r["b5"], r["b6"]) == (1, 1, 2, 2) and r["passFirst"] and r["notTurn"] and r["pub"] == "B" and r["c0"] == 19
    assert "vazia" in r["priv"] and r["secret"] and r["hidden"] and r["afterSpin"] == "2,0,1" and r["cold"] == {"turn": 1, "alive": 3, "c1": 21}
    assert r["heated"] and r["dead"] and r["seats"] == "0,2" and r["turn"] == 2 and r["reloaded"] == 1 and not r["over"]
    # treino contra bots até o fim (arma esquenta na hora)
    p.click("#bots"); p.fill("#nm", "Felipe"); p.click("#go"); p.wait_for_selector(".stage"); p.wait_for_timeout(500); p.screenshot(path="/tmp/rd_jogo.png")
    p.evaluate("G.start-=6*6e4")
    for _ in range(600):
        if p.query_selector("#again"): break
        if p.query_selector('#pass') and p.evaluate("G.turn===ME && G.players[ME].alive"): play_turn(p)
        p.wait_for_timeout(200)
    assert p.query_selector("#again"); print("treino:", p.inner_text(".status").replace("\n", " ")); p.close()
    if PEERJS:
        q = "?peerhost=localhost&peerport=9000"
        h = page(b); h.goto(URL + q); h.click("#host"); h.fill("#nm", "Felipe"); h.click("#go"); h.wait_for_selector(".code", timeout=15000); code = h.inner_text(".code"); print("sala:", code)
        gs = []
        for n in ["Ana", "Bia", "Caio"]:
            g = page(b); g.goto(URL + q + "#sala-" + code); g.click("#joinHash"); g.fill("#nm", n); g.click("#go"); g.wait_for_selector("text=Esperando", timeout=15000); gs.append(g)
        h.wait_for_selector("#start:not([disabled])"); h.click("#hm-"); h.click("#hm-"); gs[0].wait_for_selector("text=esquenta em 1:00"); h.screenshot(path="/tmp/rd_sala.png"); h.click("#start")
        for g in gs: g.wait_for_selector(".stage")
        allp = [h] + gs
        # um segredo só aparece para quem espiou
        t = next(x for x in allp if x.query_selector("#pass") and "Sua vez" in x.inner_text(".status"))
        t.click('[data-a="peekSec"]'); t.click('[data-s="1"]'); t.wait_for_selector(".toast"); print("segredo:", t.inner_text(".toast"))
        time.sleep(.5); assert not any(o.query_selector("circle[stroke-dasharray='4 4']") for o in allp if o is not t)
        t.click("#pass"); h.evaluate("G.start-=2*6e4"); time.sleep(1.2); assert "quente" in gs[1].inner_text(".heat"); gs[1].screenshot(path="/tmp/rd_quente.png")
        for _ in range(400):
            if h.query_selector("#again"): break
            for x in allp:
                if x.query_selector("#pass") and "Sua vez" in x.inner_text(".status"): play_turn(x); break
            time.sleep(.25)
        for x in allp: x.wait_for_selector(".win", timeout=10000)
        print("online:", [x.inner_text(".win") for x in allp])
    b.close()
  print("erros:", errors); assert not errors
finally:
    srv.terminate()
