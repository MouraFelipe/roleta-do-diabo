# Roleta do Diabo

Roleta russa de 3 a 6 jogadores, com moedas para espiar e manipular o tambor. Feito para jogar online com amigos (sala com código, até 6 pessoas). O treino contra bots funciona offline.

## Regras
- De 3 a 6 jogadores. Cada câmara do tambor aponta para um jogador. Até 4 jogadores: 1 bala. Com 5 ou 6: 2 balas, em posições aleatórias.
- Cada um joga na sua vez, em ordem. Na vez, é obrigatório fazer pelo menos 1 ação antes de passar.
- Todos começam com 5 moedas e ganham +1 no começo de cada vez.
- Espiar público (1): escolhe a câmara de alguém e todos veem se tem bala.
- Espiar secreto (3): só quem espiou vê. Pode contar para um aliado ou mentir.
- Esconder as balas (6): apaga o que os outros sabem (público e secreto); quem escondeu continua sabendo. Pode combinar com outra ação na mesma vez.
- Girar 1 casa (2) · girar 2 casas (3) · voltar 1 casa (4) · voltar 2 casas (5).
- A arma esquenta depois de um tempo que o dono da sala ajusta de 30 s a 15 min (padrão 2 min). Depois disso, ao passar a vez, ela dispara na câmara de quem passou. Com bala, ele sai e a bala é gasta. Quando as balas acabam, o tambor é recarregado.
- O último vivo vence. Alianças são combinadas fora do jogo.

## Técnico
- Tudo em `index.html`. Preços em `COST`; moedas iniciais, moedas por vez e tempo até esquentar em `DEF`.
- Online: PeerJS (WebRTC), quem cria a sala roda o jogo; quem cai é substituído por um bot e pode voltar.
- Offline: `sw.js` guarda o jogo no celular; dá para instalar como app.
- Teste: `python tests/test_jogo.py <caminho do peerjs.min.js>` com um servidor PeerJS local na porta 9000.
