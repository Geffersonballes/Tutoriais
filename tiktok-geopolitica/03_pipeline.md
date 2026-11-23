# Pipeline automático — "Peça por Peça" (TikTok de geopolítica)

## Organograma dos agentes

```
                         ┌──────────────────────┐
                         │   supervisor-geral   │  orquestra, aplica portões
                         └──────────┬───────────┘
   PESQUISA                         │                       PRODUÇÃO
 ┌──────────────────────┐           │          ┌──────────────────────────┐
 │ cacador-de-noticias  │           │          │ diretor-de-arte          │
 │  ├ noticias-agencias-│           │          │ narrador (ElevenLabs)    │
 │  │  globais          │           │          │ editor-de-video (ffmpeg) │
 │  ├ noticias-regionais│           │          └──────────────────────────┘
 │  └ noticias-brasil   │           │
 │ tradutor-de-fontes   │           │           REVISÃO / SUPERVISÃO
 │ editor-de-pauta      │           │          ┌──────────────────────────┐
 └──────────────────────┘           │          │ verificador-de-fatos  ⛔ │
   ROTEIRO                          │          │ critico-de-retencao      │
 ┌──────────────────────┐           │          │ revisor-de-portugues     │
 │ roteirista           │           │          │ revisor-de-conformidade⛔│
 └──────────────────────┘           │          │ controle-de-qualidade ⛔ │
   DISTRIBUIÇÃO                     │          └──────────────────────────┘
 ┌──────────────────────┐           │
 │ publicador (Metricool)│◄── 👤 aprovação humana obrigatória
 │ analista-de-desempenho│ (Windsor, tiktok_organic)
 └──────────────────────┘
```
⛔ = tem poder de veto.

## Fluxo de um vídeo

| Etapa | Agente | Entrada | Saída |
|---|---|---|---|
| 1 | cacador-de-noticias (+3 subagentes em paralelo) | — | `noticias/AAAA-MM-DD_radar.md` |
| 2 | editor-de-pauta | radar | pauta + elos + afirmações |
| 3 | tradutor-de-fontes | fontes estrangeiras | trechos em pt-BR |
| 4 | verificador-de-fatos ⛔ | afirmações | `checagem.md` |
| 5 | roteirista ↔ critico-de-retencao (≤ 2 rodadas) | pauta checada | `roteiro.md` |
| 6 | revisor-de-portugues | roteiro | `narracao_tts.txt`, legenda do post |
| 7 | revisor-de-conformidade ⛔ | roteiro | aprovado/reprovado |
| 8 | diretor-de-arte | roteiro | `storyboard.md`, `cenas.json` |
| 9 | narrador | narracao_tts.txt | `narracao.mp3`, `palavras.json` |
| 10 | geração/render das cenas | cenas.json | clipes por cena |
| 11 | editor-de-video | clipes + áudio | `final.mp4`, `capa.jpg` |
| 12 | controle-de-qualidade ⛔ + verificador-de-fatos (2ª passada) | final.mp4 | aprovado |
| 13 | 👤 dono do perfil | vídeo + legenda | "APROVADO PELO DONO" |
| 14 | publicador | aprovado | post agendado no Metricool |
| 15 | analista-de-desempenho (48 h / 7 d) | métricas Windsor | `aprendizados.md` |

## Como gerar as imagens no estilo low-poly
Recomendação, em ordem de consistência:
1. **Blender + Python (recomendado):** uma biblioteca fixa de modelos low-poly (cidade, radar,
   caminhão, avião, navio, mapa-múndi) com licença livre (CC0), cenas montadas por script a partir
   do `cenas.json`. Mesmo visual todo dia, 100 % automatizável, custo zero por vídeo.
2. **Geração por IA (imagem → vídeo curto)** para cenas pontuais: mais rápida, menos consistente;
   sempre com `isAigc: true`.
3. **Canva** para cartão final e infográficos numéricos.

## Automação
- **Frequência sugerida:** 1 vídeo por dia no início (qualidade > volume), depois 2/dia.
- **Agendamento:** uma tarefa agendada do Claude Code roda o `supervisor-geral` todo dia de
  manhã; ele produz o vídeo e para no portão humano, avisando que há um vídeo para aprovar.
- **Publicação:** Metricool (o Windsor só lê métricas do TikTok; não tem ação de publicar).

## Regras inegociáveis do nicho
- Nada de imagens reais de vítimas ou violência gráfica; tudo estilizado.
- Atribuir posições ("segundo Moscou…", "Kiev afirma…"); nunca torcer por um lado.
- Fato atual só com 2 fontes independentes; número sempre com fonte.
- Rótulo de conteúdo gerado por IA ligado.
- Copiamos a **estrutura** do vídeo de referência, não a marca, o personagem nem as cores exatas dele.
