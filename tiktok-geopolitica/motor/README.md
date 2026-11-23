# Motor de produção (Blender + Python + ffmpeg)

Pré-requisitos no container: Blender 4.2 LTS (`/opt/blender-4.2.3-linux-x64`), `libegl1 libgl1 libegl-mesa0 libgl1-mesa-dri`,
`pip install faster-whisper pillow`, ffmpeg.

| Arquivo | Função |
|---|---|
| `lowpoly.py` | Biblioteca de modelos e animação low-poly (cidade, mísseis, drones, radar, aviões, caminhões, bonecos, explosões, fumaça). Reutilizável em todos os vídeos. |
| `alinhar.py` | Alinha o texto da narração com os tempos do Whisper → `legendas.json` (palavra a palavra, com índice da cena). |
| `cena_<tema>.py` | A "decupagem" de um vídeo em código: o que aparece em cada cena, sincronizado com as palavras da narração. |
| `compor.py` | Junta os quadros do Blender + legenda palavra a palavra + rótulos amarelos + pílulas + CTA + selo de IA + áudio → `final.mp4`. |

## Passo a passo de um vídeo
```bash
P=tiktok-geopolitica/producao/<pasta>
# 1. narração (ElevenLabs) -> $P/narracao.mp3 ; texto em $P/narracao_tts.txt
ffmpeg -i $P/narracao.mp3 -ac 1 -ar 16000 /tmp/narr.wav
python3 palavras.py /tmp/narr.wav $P/palavras.json $P/narracao_tts.txt   # Whisper com tempos por palavra
python3 tiktok-geopolitica/motor/alinhar.py $P
# 2. prévia de quadros
blender -b --factory-startup -P tiktok-geopolitica/motor/cena_<tema>.py -- $P preview 5,20,40
# 3. render completo (4 processos em paralelo)
blender -b --factory-startup -P tiktok-geopolitica/motor/cena_<tema>.py -- $P range 1,1100   # ... e os outros intervalos
# 4. composição final
python3 tiktok-geopolitica/motor/compor.py $P $P/grafismos.json
```
