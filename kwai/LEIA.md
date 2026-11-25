# Kwai — Peça por Peça (decisão do dono, 25/11)

O Kwai não tem API de publicação nem integração no Metricool, então a postagem é **manual pelo dono**. Nós deixamos tudo pronto:

- Arquivo no OneDrive: `Área de Trabalho/Kwai - Peça por Peça/Kwai_postagens.txt`
  - driveId `49EB6D02466CAE02`, pasta `49EB6D02466CAE02!s7e2cf7b368e94d16a1c6efe93cbe5732`, arquivo `49EB6D02466CAE02!s81675d6a3fd94c94a59f9ba5d70fdd5c`.
- O conector Microsoft 365 só aceita arquivos de até 1 MB, e o Google Drive daqui só aceita até 10 MB. Por isso os vídeos NÃO vão para a pasta: cada item tem o link público do Picsart (gcdn.picsart.com) para baixar.

## A cada vídeo novo agendado (games e guerra)
1. Acrescente ao fim de `kwai/fila.json`: `[série, título curto, pasta, url_picsart, produto sugerido]` — produto de tecnologia/informática ligado ao tema, com o termo de busca do Kwai Shop (decisão do dono 25/11: link de venda em todo vídeo). Use a mesma URL do Picsart usada no Metricool.
2. Rode `python3 kwai/gerar_doc.py`.
3. Regrave o OneDrive com `sharepoint_update_file` (itemId acima) e o conteúdo de `kwai/Kwai_postagens.txt`.
4. Faça commit.

Pule os vídeos que só fazem sentido no TikTok (ex.: o da LIVE do TikTok).
