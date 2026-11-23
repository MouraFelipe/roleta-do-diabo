# Roleta do Diabo

Roleta russa de 3 a 6 jogadores, com moedas para espiar e manipular o tambor. Funciona offline (contra bots ou passando o celular) e online (sala com código, até 6 pessoas).

## Regras
- O tambor tem 6 câmaras e 1 bala. Na sua vez, você compra ações e depois puxa o gatilho.
- Todos começam com 5 moedas. Quem sobrevive ganha +1 moeda e o tambor anda 1 casa.
- Espiar público (1): todos veem se a câmara atual tem bala.
- Espiar secreto (3): você escolhe a câmara e só você vê.
- Girar 1 casa (2) · girar 2 casas (3) · voltar 1 casa (4) · voltar 2 casas (5).
- Quando todos já sabem onde está a bala, o Diabo recarrega o tambor.
- Quem leva o tiro sai e o tambor é recarregado. O último vivo vence.

## Técnico
- Tudo em `index.html`. Preços em `COST` e moedas iniciais/prêmio em `DEF`.
- Online: PeerJS (WebRTC), quem cria a sala roda o jogo; quem cai é substituído por um bot e pode voltar.
- Offline: `sw.js` guarda o jogo no celular; dá para instalar como app.
- Teste: `python tests/test_jogo.py <caminho do peerjs.min.js>` com um servidor PeerJS local na porta 9000.
