# Fila de render no PC do dono (GTX 1660 Super)

O PC do dono renderiza **todos os quadros (30 FPS reais) em 1080x1920** com a GPU. As sessões da nuvem só preparam e agendam.

## Sessões da nuvem (games / guerra)
1. Prepare a pasta normalmente (roteiro, narração, palavras, legendas, grafismos, cena `.py`, `curtir.mp3` se for games) e **commite tudo** (menos frames/ e mp4).
2. Crie `render_fila/pendente/<data>_<tema>.json`: `{"pasta": "...", "cena": "tiktok-geopolitica/motor/cena_x.py", "env": {"REALISTA": "1"}, "sessao": "games", "criado": "<agora>"}`, commit + push.
3. Espere `render_fila/pronto/<id>.json` (git fetch a cada ~5 min). `status: ok` → use a `url` (Picsart) no Metricool. `status: erro` → renderize na nuvem como antes (PASSO=2).
4. **Plano B:** se ninguém pegar o pedido em 20 min (ele continua em `pendente/`), apague o pedido e renderize na nuvem como antes. Se ficar em `em_andamento/` por mais de 3 h, idem.
5. QC: baixe a URL e faça a folha de contato como sempre antes de agendar.

## No PC (uma vez)
```
cd C:\Render
git clone -b claude/nifty-noether-jtt32a https://github.com/Geffersonballes/Tutoriais.git
cd Tutoriais
python -m pip install pillow numpy scipy edge-tts
winget install Gyan.FFmpeg
python render_fila\worker.py
```
Deixe o terminal aberto. Blender 4.2 LTS instalado no caminho padrão (ou defina `BLENDER`).
