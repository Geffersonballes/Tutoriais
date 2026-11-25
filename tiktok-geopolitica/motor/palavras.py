"""Transcreve a narração com tempos por palavra (faster-whisper).
Uso: python3 palavras.py <audio.wav 16k mono> <saida.json> <texto_roteiro.txt>
Por padrão usa prompt CURTO (só nomes próprios do roteiro) e condition_on_previous_text=False:
o roteiro inteiro como initial_prompt fazia o Whisper pular o começo do áudio (backlog 25/11).
PROMPT_LONGO=1 volta ao comportamento antigo. No fim compara o nº de palavras com o roteiro."""
import sys,os,re,json,wave,numpy as np
from faster_whisper import WhisperModel
w=wave.open(sys.argv[1]);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
m=WhisperModel("small",device="cpu",compute_type="int8")
txt=open(sys.argv[3]).read()
if os.environ.get("PROMPT_LONGO")=="1":
    prompt=txt[:800]; cond=True
else:
    nomes=[]
    for frase in re.split(r'[.!?\n]+',txt):
        ws=frase.split()
        for i,x in enumerate(ws):
            x=x.strip(',:;"“”')
            if i>0 and x[:1].isupper() and x not in nomes: nomes.append(x)
    prompt=", ".join(nomes)[:300]; cond=False
segs,_=m.transcribe(a,language="pt",word_timestamps=True,initial_prompt=prompt or None,condition_on_previous_text=cond)
out=[]
for s in segs:
    for x in s.words: out.append({"w":x.word.strip(),"s":round(x.start,3),"e":round(x.end,3)})
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
nr=len(txt.split())
print(len(out),"palavras transcritas /",nr,"no roteiro", "" if abs(len(out)-nr)<=max(5,nr//20) else "<<< CONFERIR: diferença grande")
print(" ".join(f"{o['w']}@{o['s']}" for o in out))
