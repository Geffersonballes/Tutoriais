# Análise do vídeo de referência — cena por cena

**Arquivo:** vídeo "Você construiu um telhado" (canal *Desmontando o Mundo*)
**Formato:** 720×1280 (9:16), 30 fps, H.264 + AAC, **2:45 (165 s)**
**Narração:** 534 palavras → **≈ 3,2 palavras/s (≈ 195 palavras/min)**, ritmo acelerado e sem pausas longas.
**Cortes secos detectados:** só 3 (10,0 s · 63,9 s · 155,4 s). O resto é **uma câmera contínua** que voa, gira e dá zoom pela cena.

Folhas de contato (1 frame por segundo): `referencia/sheet_01.jpg` a `sheet_07.jpg`.
Transcrição com tempos: `referencia/transcricao_video_referencia.txt`.

---

## 1. A fórmula narrativa (o que faz o vídeo prender)

O vídeo inteiro é **uma corrente de problema → solução → nome**. Cada elo dura 8–15 s e
sempre usa as mesmas palavras de ligação:

```
"Se você [faz o óbvio]…  [problema]."
"Então você [solução]."
"Esse(a) é o/a [NOME TÉCNICO]."        ← recompensa: o espectador aprende um termo
"Mas [a solução criou um novo problema]…"   ← gancho para o próximo elo
```

- São **11 elos** em sequência (telhas → ripas → caibros → tesouras → cumeeira → beiral → calha → rufo → subcobertura → forro → arame).
- O "Mas…" no fim de cada elo é o que segura a retenção: nunca há um ponto de parada natural.
- Fechamento: **"Parabéns! Você construiu um telhado."** — o espectador sente que *montou* algo.
- CTA binário de comentário: **"Se você sabia, comente ENGENHEIRO. Se não sabia, comente ESTAGIÁRIO."** — gera comentários fáceis (1 palavra) → algoritmo.

## 2. Linguagem visual

| Elemento | Como é feito |
|---|---|
| Estilo 3D | **Low-poly**, cores pastel saturadas, sombras suaves, céu azul com nuvens "fofas", árvores poliédricas. Nada realista. |
| Personagem | Boneco simples (camiseta amarela, calça azul). **Reage** ao problema: braços pra cima (orgulho), guarda-chuva (chuva), suando no sofá (calor). |
| Câmera | Contínua. Abre em plano geral → **dolly/zoom** até o detalhe (fresta, telha, ripa) → volta ao geral. Corte seco só para trocar de "ato". |
| Construção progressiva | Cada solução **aparece montando-se** na tela (telhas caem no lugar, ripas deslizam, tesouras surgem em amarelo). |
| Destaque do conceito | Peça nova fica **amarela/realçada** por 1–2 s antes de assumir a cor real. |
| Estado/clima como cor | Chuva (gotas azuis animadas), **noite azul = "ENCOLHE"**, **rosa/vermelho = "ESTICA"**, sol com brilho = "+50 °C", céu escuro = temporal. |
| Física exagerada | Gotas virando poças, setas vermelhas de peso ("3 TONELADAS") e o telhado **envergando** de forma caricata. |
| Vista interna | Corte para dentro da casa (sala, quadro, TV, ventilador) para mostrar o efeito no morador. |

## 3. Tipografia e grafismos (3 camadas)

1. **Legenda palavra-a-palavra** — UMA palavra por vez, no centro da tela (≈ 65 % da altura), fonte sem serifa extra-negrito (estilo *Montserrat ExtraBold*), branca com contorno/sombra preta. Troca a cada ~0,3 s, sincronizada com a fala. Palavras do NOME TÉCNICO ficam **amarelas**.
2. **Rótulo 3D do conceito** — quando o nome é revelado ("TELHAS", "RIPAS", "CAIBROS", "TESOURAS", "CUMEEIRA", "BEIRAL", "CALHA", "RUFO", "SUBCOBERTURA", "FORRO") aparece **em amarelo, itálico, preso ao objeto** na cena 3D.
3. **Pílula de etiqueta** — cápsula branca com bolinha colorida:
   - 🔴 vermelho = problema/força: *ESTICA, 3 TONELADAS, FRESTA, AR QUENTE, +50 °C*
   - 🔵 azul = estado/observação: *LAJE DE CONCRETO, ENCOLHE, GOTEIRA, ÁGUA ACUMULA, CHUVA DE LADO, PAREDE DO VIZINHO, COLCHÃO DE AR, ARAME*
4. **Infográfico numérico** — quando há número: título amarelo no topo ("30 % = SOBE 30 cm A CADA 1 m"), triângulo amarelo, régua "1 m", cota "30 cm", selo "30 %".
5. **Cartão final** — CTA em 2 linhas com aspas grandes ("ENGENHEIRO" branco / "ESTAGIÁRIO" azul) + marca do canal numa pílula escura.

## 4. Decupagem cena por cena

| # | Tempo | Narração (resumo) | Imagem / animação | Grafismo |
|---|---|---|---|---|
| 0 | 0,0–4,7 | "Se você levanta as paredes… laje reta de concreto" | Paredes sobem do chão; boneco de braços erguidos; laje cai por cima | pílula *LAJE DE CONCRETO* |
| 1 | 4,7–9,5 | "Ela fica empoçada, acha uma rachadurinha e pinga" | Zoom no teto: poças azuis crescem → **corte p/ interior**: rachadura preta + gotas caindo | *GOTEIRA* |
| 2 | 10,0–12,3 | "Então você inclina a cobertura" | Plano geral, laje inclina, água escorre; boneco com guarda-chuva | — |
| 3 | 12,3–19,7 | "Estica no sol, encolhe à noite… até rachar" | Laje fica **rosa com setas vermelhas** (dia) ↔ **azul com setas** (noite), loop; rachadura | *ESTICA* / *ENCOLHE* / *GOTEIRA* |
| 4 | 19,7–25,0 | "Peças pequenas e soltas… Essas são as TELHAS" | Laje se fragmenta em telhas vermelhas | rótulo **TELHAS** |
| 5 | 26,8–36,7 | "Água entra pela fresta… encaixa por cima da de baixo" | Macro nas telhas: frestas destacadas em amarelo; gotas entrando → telha sobrepõe, gotas escorrem | *FRESTAS*, *TELHA SOBRE TELHA* |
| 6 | 36,7–48,3 | "Se for muito deitado… 30 % de inclinação" | Telhado achatado: poças em cada telha → **corte p/ diagrama lateral** com triângulo e régua | *ÁGUA ACUMULA*, infográfico 30 % |
| 7 | 48,3–55,7 | "Telha não flutua… ripinhas… RIPAS" | Câmera atravessa a parede (sala com quadro/estante) e olha p/ cima: ripas horizontais em amarelo | rótulo **RIPAS** |
| 8 | 55,7–63,6 | "Algo pra sustentar… CAIBROS" | Madeiras verticais surgem por baixo das ripas, amarelas | rótulo **CAIBROS** |
| 9 | 63,9–84,2 | "Pesa toneladas… enverga… triângulos… TESOURAS" | Plano geral: setas de peso, estrutura **enverga** e paredes abrem → triângulos amarelos aparecem; seta vermelha empurra e nada cede | *3 TONELADAS*, rótulo **TESOURAS** |
| 10 | 84,2–93,3 | "Fresta aberta no topo… CUMEEIRA" | Close no topo, fresta pisca, telhas curvas cobrem | *FRESTA*, rótulo **CUMEEIRA** |
| 11 | 93,3–103,6 | "Água escorre grudada na parede… BEIRAL" | Parede escurece de umidade; telhado estica p/ fora | rótulo **BEIRAL** |
| 12 | 103,6–111,0 | "Canaleta na beirada… CALHA" | Macro da calha com gotas e cano até o chão | rótulo **CALHA** |
| 13 | 111,0–124,4 | "Parede mais alta… chapa dobrada… RUFO" | Parede do vizinho; água escorrendo; chapa amarela dobra sobre telhas | *PAREDE DO VIZINHO*, rótulo **RUFO** |
| 14 | 124,4–143,2 | "Chuva de lado… +50 °C… manta de alumínio… SUBCOBERTURA" | Céu escuro/temporal; depois sol com **brilho** nas telhas; telhado desmonta e manta prateada é estendida | *CHUVA DE LADO*, *+50 °C*, rótulo **SUBCOBERTURA** |
| 15 | 143,2–155,4 | "Ar quente desce… colchão de ar… FORRO" | Interior: boneco suando, bolinhas vermelhas (calor) caindo → forro fecha, calor fica em cima | *AR QUENTE*, *COLCHÃO DE AR*, rótulo **FORRO** |
| 16 | 155,4–158,1 | "Amarre as telhas da beirada com arame" | Macro: arame amarelo enrola na telha | *ARAME* |
| 17 | 158,1–165,0 | "Parabéns! Você construiu um telhado" + CTA | Plano geral final, boneco comemora | rótulo **TELHADO**, CTA ENGENHEIRO/ESTAGIÁRIO, marca |

## 5. Números-chave do formato (para replicar)

| Métrica | Valor |
|---|---|
| Duração | 2:30–2:50 (bom para o *Creator Rewards*, que exige > 1 min) |
| Elos problema→solução | 10–12, de 8–15 s cada |
| Palavras/segundo | ≈ 3,2 |
| Troca de legenda | a cada palavra (~0,3 s) |
| Evento visual novo | a cada 1–2 s (zoom, peça entrando, pílula, cor) |
| Cortes secos | 3–5 (troca de ato) |
| Primeiro frame | já mostra a ação (paredes subindo); nada de introdução |

## 6. O que vamos melhorar na nossa versão

1. **Gancho mais forte nos primeiros 2 s**: frase-choque + número na tela (o original começa morno).
2. **Mapa como "cenário base"**: em vez da casa, um globo/mapa low-poly onde as peças entram.
3. **Fontes na tela** (pílula discreta "Fonte: Reuters / AP" quando citar fato atual) — credibilidade num tema sensível.
4. **Selo "Conteúdo gerado com IA"** quando usarmos imagem/voz sintética (exigência do TikTok).
5. **Série com identidade própria**: nome, vinheta de 0,5 s e CTA próprio — *não* copiar a marca, as cores exatas nem o personagem do canal de referência; copiamos só a **estrutura**.
