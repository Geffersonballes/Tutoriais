# Backlog de melhorias (o controle de qualidade e o dono adicionam; o melhoria-continua prioriza)

| # | Área | Problema / ideia | Origem | Impacto | Esforço | Status |
|---|---|---|---|---|---|---|
| 1 | Visual C | Enquadramentos com muito chão vazio (zonas "linha do tempo" e "ping" do vídeo do servidor) — criar presets de câmera fechada (close no Pixel, plano médio, POV) | QC 23/11 | alto | baixo | feito 24/11: `camera_cartoon()` + `plano(t, centro, 'close'|'medio'|'geral')` em `cartoon.py`, usado em `cena_gta30.py` |
| 2 | Visual C | Cenários fechados e ricos (quarto gamer, arena, data center) como módulos reutilizáveis em `cartoon.py` | referência Desmontando o Mundo | alto | médio | em parte (24/11): `sala_fechada()`, `quarto_gamer()` e `data_center()` em `cartoon.py`; falta arena |
| 3 | Visual C | Placas de HUD com número dentro do cenário (tipo "ALTURA 3.860 m") | referência | médio | baixo | aberto |
| 4 | Visual B | Cena da ponte da Crimeia ficou simples; mar com ondas e ponte com arcos | QC 23/11 | baixo | baixo | aberto |
| 5 | Visual B | Cena noturna do vídeo 01 ficou escura demais | QC 23/11 | baixo | baixo | aberto |
| 6 | YouTube | Capa dos Shorts: canal verificado pelo dono em 23/11; posts passam a enviar videoCoverMilliseconds 600 | análise 23/11 | médio | baixo | feito (conferir no próximo post) |
| 7 | Estratégia | Geopolítica tem ~1 view no canal gamer do YouTube — avaliar postar geopolítica só no TikTok | análise 23/11 | alto | baixo | feito: dono decidiu em 23/11 — geopolítica só no TikTok (GTA 6 1,1 mil vs 2–3 views) |
| 8 | Composição | Legenda trocava "quatro" por "4" em "sessenta e quatro" — agora `subst` por vídeo no grafismos.json (corrigido) | QC 23/11 | baixo | baixo | feito |
| 9 | Visual C | CTA final encosta na cabeça do Pixel no close — subir CTA ou afastar a câmera no bloco final | QC 23/11 | baixo | baixo | aberto |
| — | Visual C | (corrigido 24/11) `modo_cartoon()` misturava os canais R/G/B ao converter `cor_key` → cores animadas saíam erradas/apagadas; agora grava cada canal com `index` | QC gta6-30fps | médio | baixo | feito |
| — | Composição | (corrigido 24/11) `compor.py` trocava toda palavra "trinta" por "35" (resto do vídeo 01); agora só sem `"subst"` no grafismos.json | QC gta6-30fps | alto | baixo | feito |
