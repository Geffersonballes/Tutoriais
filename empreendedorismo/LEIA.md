# Negócio Peça por Peça (nome provisório) — série de empreendedorismo

Perfil PESSOAL do Facebook do dono (monetizando). Pequeno empreendedor (MEI, comércio local, serviço).
Voz: testes com voz grátis; só a versão final aprovada vai na voz do dono no ElevenLabs (ver seção VOZ). 1 vídeo/dia após o piloto.
Entrega MANUAL: Metricool e APIs da Meta não publicam em perfil pessoal. Para cada vídeo: link do Picsart +
legenda num .txt na pasta do OneDrive "Área de Trabalho/Negócio Peça por Peça" (padrão de kwai/LEIA.md).

- motor/visual.py — identidade visual (fundo planilha, cupom, barras, número grande, legenda discreta, selo de IA)
- piloto/01-acai — "contas reais": quanto sobra de um açaí de R$ 20 no iFood
- piloto/02-ballestech — bastidores: do anúncio ao telhado (aguarda dados do dono)
Regra: todo número com 2 fontes; taxa que varia vai como faixa; custo de exemplo marcado com *.

Atualização 27/11 (sessão principal): o perfil é o "geffersonballes" (pessoal, modo profissional, monetizando).
O dono vai testar se ele aparece para conectar no Metricool (marca geffersonballes1, id 8356514); se aparecer,
a publicação vira automática. Até lá: entrega manual pelo OneDrive + instruções para agendar em lote pelo
Meta Business Suite, que agenda posts em perfil com modo profissional.
Confirmado depois: o Metricool NÃO lista o perfil. Entrega em LOTE SEMANAL (pasta por semana no OneDrive, vídeos numerados
por dia e horário, .txt com legendas e links do Picsart). Passo a passo em COMO_AGENDAR.md. Não usar a página Balles Tech.

## OneDrive (criado 27/11)
- Pasta da série: "Área de Trabalho/Negócio Peça por Peça" — itemId 49EB6D02466CAE02!s0160f499c2b24bf28f61598b31b6ea98
  - COMO_AGENDAR.txt — 49EB6D02466CAE02!sc34e81fa6544484188bbf578b8d59a4b
  - Semana 2026-11-30/ — 49EB6D02466CAE02!s43ff1b38df3b45f49b293bc2b2432726
    - Semana_2026-11-30.txt — 49EB6D02466CAE02!s1eeeb61bc3e343b59b0a1d71b0e11a5c (cópia local em entregas/)
- Vídeo 01 (açaí), aprovado pelo dono 27/11: https://gcdn.picsart.com/picsart-mcp/fe200b0b-004b-40d9-90c9-42b60592f106.mp4

## Decisões 27/11 (depois do piloto)
- Vídeo 02 (Balles Tech) reprovado: não publicar.
- O dono quer ilustrações mais intuitivas, interativas e "responsivas" (tudo reagindo à fala), 3D melhor e FOTOS REAIS.
  Fotos: só com licença livre para uso comercial (agente pesquisador-de-imagens); Google Imagens NÃO, por risco de direito
  autoral num perfil monetizado. 3D: Blender 4.2 já instalado (motor em tiktok-geopolitica/motor).
- Agentes novos: pesquisador-de-imagens, pauteiro-empreendedorismo (.claude/agents/).

## VOZ (decisão do dono, 27/11) — vale acima do que está escrito antes
- Testes e versões de aprovação: SEMPRE voz grátis (edge-tts pt-BR-AntonioNeural; rodar com SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
  e --proxy "$HTTPS_PROXY"; ajustar --rate para caber em 75 s). Não gastar ElevenLabs.
- Só a versão FINAL, já aprovada pelo dono e que vai ser postada, é regravada na voz do dono (ElevenLabs eleven_v4,
  voice Dt3IFiwrxXdZMMFz4Ai0, 1 geração) e re-renderizada.
- Vídeo 01 (açaí) liberado para postar ("pode mandar bala").

## QUALIDADE ACIMA DO TEMPO DE RENDER (decisão do dono, 27/11)
1 vídeo por dia: o render pode levar o tempo que precisar; o padrão é PROFISSIONAL.
- 3D no Blender EEVEE em 1080x1920 cheio (nada de render pequeno ampliado), 24+ amostras, luz de estúdio, profundidade de campo.
- 3D na maior parte das cenas, com movimento de câmera; gráfico 2D só por cima (etiquetas, números, legenda).
- Medido no teste: ~1 min por quadro a 24 amostras (4 núcleos). Render roda em segundo plano, por partes, salvando os quadros já
  prontos para retomar se a máquina reiniciar (mesmo esquema do render.sh/render_estado.txt dos games).
