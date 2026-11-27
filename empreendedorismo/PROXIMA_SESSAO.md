# Passagem de bastão — série "Negócio Peça por Peça" (27/11/2026)

Sessão anterior: session_01DxZEAHGZukfM3LxbjiVFRC (filha da principal session_01DxZEAGsFhNPqFvLAMQCk6V; mande resumos para a principal
com send_message). Leia antes: empreendedorismo/LEIA.md (decisões do dono), BANCOS_DE_MIDIA.md, COMO_AGENDAR.md.

## Estado
- Vídeo 01 (açaí no iFood): APROVADO e entregue no OneDrive (Semana 2026-11-30, seg 30/11 19h). Nada a fazer.
- Vídeo 02 (Balles Tech): REPROVADO. Não usar.
- Visual 2.0 aprovado pelo dono ("ficou muito legal"): 3D de produto no Blender EEVEE (motor/estudio3d.py) + etiquetas 2D por cima.
- Pautas prontas (agente pauteiro-empreendedorismo): pautas/2026-11-27_pix-x-maquininha.md e pautas/2026-11-27_corte-de-cabelo.md.
- Produção de TESTE em andamento: producao/2026-11-28_pix-x-maquininha/
  - narracao.mp3 = voz GRÁTIS (edge-tts Antonio +15%, 72 s), legendas.json alinhado, tex/ (telas sem marca), cena.py (3D animado, 9 planos).
  - Quadros de teste conferidos (teste3d_*.png, fora do git). Falta: render completo + compor.py (2D por cima) + entrega ao dono.

## Chaves novas (só valem nesta sessão nova)
- PIXABAY_API_KEY e UNSPLASH_ACCESS_KEY criadas pelo dono (variáveis de ambiente). Pexels: emissão de chaves pausada.
- Confira: `[ -n "$PIXABAY_API_KEY" ] && echo ok`. Teste 1 busca em cada banco antes de usar.

## Próximos passos
1. Fotos: rode o agente pesquisador-de-imagens para o vídeo do Pix (abertura: balcão com maquininha; cena 8: mãos contando dinheiro),
   agora com Pixabay e Unsplash. Crédito do Unsplash na legenda.
2. PRÉVIA RÁPIDA para aprovação (economiza horas): `AMOSTRAS=8` e resolução 540x960 (edite config_render) ou `render 1 FIM 2`,
   depois escreva compor.py (base: motor/video.py + motor/visual.py) com as etiquetas que entram na fala de cada taxa, contador
   "sobra de R$ 100", barras, linha das 12 parcelas, ranking final, balões do CTA, selo de IA, chip de fontes e legenda.
   Mande ao dono com SendUserFile.
3. Aprovado → VOZ FINAL no ElevenLabs (eleven_v4, Dt3IFiwrxXdZMMFz4Ai0, 1 geração; prompt com etiquetas [curious] etc.),
   palavras.py + alinhar.py (os tempos mudam!), e só então o render FINAL 1080x1920 a 16–24 amostras
   (~23 s por quadro a 16 amostras → ~14 h; rode em segundo plano: `nohup blender -b -P cena.py -- render > render.log 2>&1 &`;
   o render retoma sozinho porque pula quadros prontos).
4. Entrega: Picsart (picsart_upload_local_files + curl) → .txt da semana no OneDrive (pasta "Semana AAAA-MM-DD"; ids em LEIA.md).
5. Depois: propor ao dono a ROTINA DIÁRIA (horário e tema por dia da semana, incluindo 1 pauta de normas fiscais/leis por semana)
   e criar o agendamento com create_trigger ligado à sessão; mandar resumo à sessão principal.

## Regras que não podem ser esquecidas
- Testes com voz grátis; ElevenLabs só na versão final aprovada (cerca de 1.250 créditos por vídeo; avisar se o saldo < 15 mil).
- Todo número com 2 fontes; faixa quando varia; exemplo marcado com *; fonte na tela; pergunta no fim para comentários.
- Selo "Conteúdo gerado com IA"; nada de Google Imagens; sem marcas em destaque.
- Postagem é MANUAL pelo dono no perfil pessoal (Meta Business Suite); nunca publicar por ferramenta.
- Branch claude/nifty-noether-jtt32a compartilhada: `git fetch origin claude/nifty-noether-jtt32a && git merge --no-edit FETCH_HEAD`
  antes de cada push. Sem PR, sem force-push.
