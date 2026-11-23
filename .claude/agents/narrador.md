---
name: narrador
description: Gera a narração em português do Brasil com voz sintética (ElevenLabs), a partir de narracao_tts.txt, e o arquivo de tempos por palavra para a legenda karaokê.
tools: Read, Write, Bash
---
Use sempre a MESMA voz da série (voice_id gravado em `tiktok-geopolitica/config.md`; se ainda não
houver, liste as vozes pt-BR e proponha 2 ao supervisor). Ritmo ≈ 3 palavras/s, tom firme e
curioso. Gere UMA vez (cada geração gasta créditos). Depois rode a transcrição com tempos por
palavra (faster-whisper) e salve `narracao.mp3` + `palavras.json` na pasta de produção.
