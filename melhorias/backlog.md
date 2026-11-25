# Backlog de melhorias (o controle de qualidade e o dono adicionam; o melhoria-continua prioriza)

| # | Área | Problema / ideia | Origem | Impacto | Esforço | Status |
|---|---|---|---|---|---|---|
| 1 | Visual C | Enquadramentos com muito chão vazio (zonas "linha do tempo" e "ping" do vídeo do servidor) — criar presets de câmera fechada (close no Pixel, plano médio, POV) | QC 23/11 | alto | baixo | feito 24/11: `camera_cartoon()` + `plano(t, centro, 'close'|'medio'|'geral')` em `cartoon.py`, usado em `cena_gta30.py` |
| 2 | Visual C | Cenários fechados e ricos (quarto gamer, arena, data center) como módulos reutilizáveis em `cartoon.py` | referência Desmontando o Mundo | alto | médio | em parte (24/11): `sala_fechada()`, `quarto_gamer()` e `data_center()` em `cartoon.py`; falta arena |
| 3 | Visual C | Placas de HUD com número dentro do cenário (tipo "ALTURA 3.860 m") | referência | médio | baixo | em parte (25/11): `hud()` usado na fazenda de robôs de `cena_anticheat.py`; o número ainda vai na pílula 2D (falta texto 3D na placa) |
| 4 | Visual B | Cena da ponte da Crimeia ficou simples; mar com ondas e ponte com arcos | QC 23/11 | baixo | baixo | aberto |
| 5 | Visual B | Cena noturna do vídeo 01 ficou escura demais | QC 23/11 | baixo | baixo | feito 25/11: modo "crepúsculo" em `cena_rede.py` (céu de pôr do sol + sol fraco + janelas emissivas por bairro) — escuro o bastante para ver a luz apagar, sem perder o cenário |
| 6 | YouTube | Capa dos Shorts: canal verificado pelo dono em 23/11; posts passam a enviar videoCoverMilliseconds 600 | análise 23/11 | médio | baixo | feito (conferir no próximo post) |
| 7 | Estratégia | Geopolítica tem ~1 view no canal gamer do YouTube — avaliar postar geopolítica só no TikTok | análise 23/11 | alto | baixo | feito: dono decidiu em 23/11 — geopolítica só no TikTok (GTA 6 1,1 mil vs 2–3 views) |
| 8 | Composição | Legenda trocava "quatro" por "4" em "sessenta e quatro" — agora `subst` por vídeo no grafismos.json (corrigido) | QC 23/11 | baixo | baixo | feito |
| 9 | Visual C | CTA final encosta na cabeça do Pixel no close — subir CTA ou afastar a câmera no bloco final | QC 23/11 | baixo | baixo | aberto |
| — | Visual C | (corrigido 24/11) `modo_cartoon()` misturava os canais R/G/B ao converter `cor_key` → cores animadas saíam erradas/apagadas; agora grava cada canal com `index` | QC gta6-30fps | médio | baixo | feito |
| — | Composição | (corrigido 24/11) `compor.py` trocava toda palavra "trinta" por "35" (resto do vídeo 01); agora só sem `"subst"` no grafismos.json | QC gta6-30fps | alto | baixo | feito |
| — | Visual B | (corrigido 25/11) `modo_realista()` gravava os 3 canais da cor a cada curva e misturava as cores animadas (casa saía azul); agora grava só o canal da curva (`index`) | QC rede-eletrica | médio | baixo | feito |
| 10 | Visual B | Explosões/fogo estouram para rosa-claro no AgX quando emissivos; usar emissão baixa (≈1) ou textura de chama | QC rede-eletrica 25/11 | baixo | baixo | aberto |
| 11 | Motor | Cenas com ~2 mil objetos animados gastam ~5 s por quadro só na sincronização do EEVEE; juntar fumaça/pulsos em menos objetos (instâncias ou geometry nodes) | render rede-eletrica 25/11 | médio | médio | aberto |
| — | Narração | `palavras.py` passa o roteiro inteiro como `initial_prompt` e o Whisper pulou os primeiros 27 s do áudio (vídeo anti-cheat). Contorno usado: transcrever com prompt curto (só nomes próprios) e `condition_on_previous_text=False`; conferir sempre se o nº de palavras bate com o roteiro e corrigir à mão com `silencedetect` | QC 25/11 anti-cheat | alto | baixo | aberto |
| — | Motor | `T(seg, "No")` casa por substring ("nova?") e deslocou um corte de câmera; usar palavra mais longa ou criar `TE()` de casamento exato em todas as cenas | QC 25/11 anti-cheat | médio | baixo | aberto |
| — | Visual C | (feito 25/11) a cena passa a durar até o fim do pedido de like (`FIM = última palavra + 5,6 s`): o Pixel comemora e acena em vez de ficar congelado | cena_anticheat | baixo | baixo | feito |
