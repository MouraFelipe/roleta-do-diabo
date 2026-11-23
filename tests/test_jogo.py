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
      o.notTurn=act(G,1,{t:'peekPub',s:0}).err;
      act(G,0,{t:'peekPub',s:1}); o.pub=G.pub[1]; o.c0=G.players[0].coins;
      const s=act(G,0,{t:'peekSec',s:2}); o.priv=s.priv; o.secret=G.players[0].know[2]==='V' && !G.players[1].know[2];
      o.hidden=!JSON.stringify(viewFor(G,1)).includes('"b"');
      act(G,0,{t:'spin',n:1}); o.afterSpin=G.cyl.map(c=>c.id).join(); // a câmara 1 (bala) foi para o lugar 2
      act(G,0,{t:'pass'}); o.cold={turn:G.turn, alive:G.players.filter(p=>p.alive).length, c1:G.players[1].coins};
      G.start-=6*6e4; act(G,1,{t:'spin',n:-1}); o.heated=G.heated;            // bala volta para o lugar 1 (jogador 1)
      G.cfg.devil=false; act(G,1,{t:'pass'}); o.noShotOnPass=G.players.every(p=>p.alive) && G.phase==='play';
      act(G,2,{t:'pass'}); o.shotPhase=G.phase; G.sh.who=1; G.sh.at=0; stepShot(G); o.aimed=G.aim; G.sh.at=0; stepShot(G);
      o.dead=!G.players[1].alive; o.seats=G.seats.join(); o.over=G.over; o.winners=G.result&&G.result.winners.join();
      const H=newGame(L(3)); H.turn=0; H.players.forEach(p=>p.coins=20); H.pub[0]='V'; H.players[0].know[1]='B'; H.players[1].know[2]='V';
      act(H,0,{t:'hide'}); o.hide={pub:Object.keys(H.pub).length, mine:JSON.stringify(H.players[0].know), other:Object.keys(H.players[1].know).length, coins:H.players[0].coins};
      // giro cego: todos perdem o que sabiam
      const B=newGame(L(4),{devil:false}); B.players.forEach(p=>p.coins=20); B.pub[0]='V'; B.players[B.turn].know[1]='B'; act(B,B.turn,{t:'blind'});
      o.blind={pub:Object.keys(B.pub).length, know:B.players.every(p=>!Object.keys(p.know).length), bullets:bulletsLeft(B)};
      // volta completa: o final passa por cada um até a última bala
      const V2=newGame(L(5),{mode:'volta',heatSec:1}); V2.start-=5e3; act(V2,V2.turn,{t:'peekPub',s:0}); o.vPhase=V2.phase;
      for(let k=0;k<40 && !V2.over;k++){ V2.fin.at=0; stepFinale(V2); }
      o.volta={over:V2.over, dead:V2.players.filter(p=>!p.alive).length, left:bulletsLeft(V2)};
      // traidor: vê as balas; acusação certa revela
      const T=newGame(L(4),{mode:'traidor'}); T.players.forEach(p=>p.coins=20); const tv=viewFor(T,T.traitor), ov=viewFor(T,(T.traitor+1)%4);
      o.tSees=Object.keys(tv.know).length===4 && tv.isTraitor && ov.traitor===-1 && Object.keys(ov.know).length===0;
      const acc=T.turn===T.traitor ? T.seats.find(x=>x!==T.traitor) : T.turn; T.turn=acc; act(T,acc,{t:'accuse',target:T.traitor}); o.tRev=T.revealed && T.players[T.traitor].coins===0;
      // leilão: depois de uma volta, maior lance vê tudo e todos pagam
      const A=newGame(L(3),{mode:'leilao'}); A.players.forEach(p=>p.coins=10);
      for(let k=0;k<3;k++){ act(A,A.turn,{t:'peekPub',s:0}); act(A,A.turn,{t:'pass'}); }
      o.aPhase=A.phase; const [x,y,z]=A.seats; bid(A,x,5); bid(A,y,2); const cx=A.players[x].coins; bid(A,z,0);
      o.auc={phase:A.phase, win:Object.keys(A.players[x].know).length===3, paid:A.players[x].coins===cx-5 && A.priv.length===1};
      // fim da volta: o Diabo gira às cegas e apaga o que se sabia
      const D=newGame(L(3)); D.pub[0]='V'; D.players[0].know[1]='B'; const ids=D.cyl.map(c=>c.id).join();
      for(let k=0;k<3;k++) act(D,D.turn,{t:'pass'});
      o.devil={pub:Object.keys(D.pub).length, know:D.players.every(p=>!Object.keys(p.know).length), newIds:D.cyl.map(c=>c.id).join()!==ids, bullets:bulletsLeft(D)};
      const E=newGame(L(3),{devil:false}); E.pub[0]='V'; for(let k=0;k<3;k++) act(E,E.turn,{t:'pass'}); o.devilOff=E.pub[0]==='V'; o.b8=bulletsLeft(newGame(L(8))); o.b10=bulletsLeft(newGame(L(10)));
      const T2=newGame(L(3),{mode:'traidor'}); T2.pub[0]='V'; for(let k=0;k<3;k++) act(T2,T2.turn,{t:'pass'});
      const other=(T2.traitor+1)%3; o.tDv={phase:T2.phase, wrong:!!devilChoice(T2,other,true).err, mine:viewFor(T2,T2.traitor).dv.mine, notMine:viewFor(T2,other).dv.mine};
      act(T2,T2.traitor,{t:'devil',spin:false}); o.tDv.kept=T2.pub[0]==='V' && T2.phase==='play';
      return o; }""")
    print("regras:", r); assert r["b8"]==3 and r["b10"]==3 and r["tDv"]=={"phase":"devil","wrong":True,"mine":True,"notMine":False,"kept":True} and r["devilOff"] and r["devil"]=={"pub":0,"know":True,"newIds":True,"bullets":1}; assert r["blind"]=={"pub":0,"know":True,"bullets":1} and r["vPhase"]=="finale" and r["volta"]["over"] and r["volta"]["left"]==0 and r["volta"]["dead"]==2 and r["tSees"] and r["tRev"] and r["aPhase"]=="auction" and r["auc"]=={"phase":"play","win":True,"paid":True}; assert r["hide"] == {"pub": 0, "mine": '{"0":"V","1":"B"}', "other": 0, "coins": 14}
    assert (r["b3"], r["b4"], r["b5"], r["b6"]) == (1, 1, 2, 2) and r["notTurn"] and r["pub"] == "B" and r["c0"] == 19
    assert "vazia" in r["priv"] and r["secret"] and r["hidden"] and r["afterSpin"] == "2,0,1" and r["cold"] == {"turn": 1, "alive": 3, "c1": 21}
    assert r["noShotOnPass"] and r["shotPhase"]=="shot" and r["aimed"]==1 and r["heated"] and r["dead"] and r["seats"] == "0,2" and r["over"] and r["winners"] == "0,2"   # acabou a bala, acabou a partida
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
        h.wait_for_selector("#start:not([disabled])"); h.click("[id='hm-']"); gs[0].wait_for_selector("text=esquenta em 0:30"); h.click("#dv"); gs[0].wait_for_selector("text=desligado"); h.click("#dv"); gs[0].wait_for_selector("b:text-is('ligado')"); h.screenshot(path="/tmp/rd_sala.png"); h.click("#start")
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
