"""Transcreve a narração com tempos por palavra (faster-whisper). Uso: python3 palavras.py <audio.wav 16k mono> <saida.json> <texto_roteiro.txt>"""
import sys,json,wave,numpy as np
from faster_whisper import WhisperModel
w=wave.open(sys.argv[1]);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
m=WhisperModel("small",device="cpu",compute_type="int8")
txt=open(sys.argv[3]).read()
segs,_=m.transcribe(a,language="pt",word_timestamps=True,initial_prompt=txt[:800])
out=[]
for s in segs:
    for x in s.words: out.append({"w":x.word.strip(),"s":round(x.start,3),"e":round(x.end,3)})
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
print(len(out)); print(" ".join(f"{o['w']}@{o['s']}" for o in out))
