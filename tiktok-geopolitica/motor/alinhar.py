"""Alinha o texto do roteiro (narracao_tts.txt) com os tempos do Whisper (palavras.json).
Gera legendas.json: lista de {w, s, e, seg} com a grafia do roteiro e o índice do parágrafo (= cena)."""
import json, re, sys, difflib, unicodedata
pasta = sys.argv[1]
txt = open(f"{pasta}/narracao_tts.txt", encoding="utf-8").read().strip().split("\n")
wh = json.load(open(f"{pasta}/palavras.json", encoding="utf-8"))
norm = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
NUM = {"4": "quatro", "5": "cinco", "100": "cem", "sem": "cem", "mais": "mas"}
tok = []
for i, par in enumerate(txt):
    for w in par.split():
        tok.append({"w": w, "seg": i})
a = [norm(t["w"]) for t in tok]
b = [NUM.get(norm(x["w"]), norm(x["w"])) for x in wh]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        tok[blk.a + k]["s"] = wh[blk.b + k]["s"]; tok[blk.a + k]["e"] = wh[blk.b + k]["e"]
# interpola os que não casaram
for i, t in enumerate(tok):
    if "s" not in t:
        j = i - 1
        prev = tok[j]["e"] if j >= 0 and "e" in tok[j] else 0.0
        k = i + 1
        while k < len(tok) and "s" not in tok[k]: k += 1
        nxt = tok[k]["s"] if k < len(tok) else prev + 0.4
        n = k - i
        t["s"] = prev + (nxt - prev) * 0 / max(n, 1)
        step = (nxt - prev) / (n + 1)
        for m in range(n):
            tok[i + m]["s"] = round(prev + step * m, 3); tok[i + m]["e"] = round(prev + step * (m + 1), 3)
json.dump(tok, open(f"{pasta}/legendas.json", "w", encoding="utf-8"), ensure_ascii=False)
segs = {}
for t in tok: segs.setdefault(t["seg"], [t["s"], t["e"]]); segs[t["seg"]][1] = t["e"]
for k, v in segs.items(): print(k, v, " ".join(x["w"] for x in tok if x["seg"] == k)[:50])
print("não casadas:", sum(1 for i,t in enumerate(tok) if a[i] not in b))
