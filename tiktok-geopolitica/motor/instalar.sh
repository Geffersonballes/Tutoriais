#!/usr/bin/env bash
# Prepara a máquina para o motor de vídeo (idempotente). Uso: bash tiktok-geopolitica/motor/instalar.sh
set -e
if ! command -v blender >/dev/null 2>&1; then
  cd /opt && curl -sSfL -o blender.tar.xz https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz
  tar xf blender.tar.xz && rm blender.tar.xz && ln -sf /opt/blender-4.2.3-linux-x64/blender /usr/local/bin/blender
fi
if [ ! -e /usr/lib/x86_64-linux-gnu/libEGL.so.1 ]; then
  apt-get update -q >/dev/null && apt-get install -y -q libegl1 libgl1 libegl-mesa0 libgl1-mesa-dri >/dev/null
fi
python3 -c "import faster_whisper" 2>/dev/null || pip install -q faster-whisper pillow
command -v ffmpeg >/dev/null || (apt-get update -q >/dev/null && apt-get install -y -q ffmpeg >/dev/null)
blender --version | head -1
