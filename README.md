# Roleta do Diabo

Roleta russa de 3 a 6 jogadores, com moedas para espiar e manipular o tambor. Feito para jogar online com amigos (sala com código, até 6 pessoas). O treino contra bots funciona offline.

## Regras (base de todos os modos)
- De 3 a 6 jogadores. Cada câmara do tambor aponta para um jogador. Até 4 jogadores: 1 bala. Com 5 ou 6: 2 balas.
- Cada um joga na sua vez, em ordem, e faz pelo menos 1 ação antes de passar.
- Todos começam com 5 moedas e ganham +1 no começo de cada vez.
- Ações: espiar público (1), espiar secreto (3), esconder as balas (6), giro cego (7), girar 1/2 (2/3), voltar 1/2 (4/5).
- A arma esquenta depois de um tempo que o dono da sala ajusta (30 s a 15 min, padrão 2 min).
- A partida acaba quando a última bala é disparada. Quem estiver vivo vence; o mais rico é o campeão.

## Modos
- **Padrão:** depois que a arma esquenta, ela dispara em quem passa a vez.
- **Volta completa:** ninguém leva tiro antes. Quando a arma esquenta, ela aponta para cada um, em ordem, até a última bala.
- **Traidor oculto:** um jogador secreto é o servo do Diabo e vê todas as balas. Ele vence se sobreviver sem ser descoberto. Acusar custa 4: se acertar, ele perde todas as moedas.
- **Leilão da bala:** a cada volta da mesa, lances escondidos. O maior lance vê onde estão todas as balas; todos pagam o próprio lance; empate, ninguém vê.

## Técnico
- Tudo em `index.html`. Preços em `COST`; moedas iniciais, moedas por vez e tempo até esquentar em `DEF`.
- Online: PeerJS (WebRTC), quem cria a sala roda o jogo; quem cai é substituído por um bot e pode voltar.
- Offline: `sw.js` guarda o jogo no celular; dá para instalar como app.
- Teste: `python tests/test_jogo.py <caminho do peerjs.min.js>` com um servidor PeerJS local na porta 9000.
