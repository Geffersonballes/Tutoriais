"""Base de render dos vídeos da série: lê legendas.json, monta a legenda (com números curtos),
mixa voz + trilha + efeitos e codifica o MP4 com anti-borda.
Uso típico num render.py:
    V = Video(AQUI, subst=[("vinte reais", "R$ 20"), ...])
    def quadro(t): ...  (usa V.ini, V.tw, V.pal)
    V.rodar(quadro, cortes=[...], pops=[...])"""
import os, sys, re, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tiktok-geopolitica", "motor"))
from visual import *

FPS = 30
def norm(w): return re.sub(r"[^\wÀ-ÿ]", "", w.lower())

class Video:
    def __init__(self, pasta, subst=(), cauda=1.6):
        self.pasta = pasta
        self.leg = json.load(open(f"{pasta}/legendas.json", encoding="utf-8"))
        self.nseg = max(x["seg"] for x in self.leg) + 1
        self.ini = {k: min(x["s"] for x in self.leg if x["seg"] == k) for k in range(self.nseg)}
        self.fim = {k: max(x["e"] for x in self.leg if x["seg"] == k) for k in range(self.nseg)}
        self.dur = self.fim[self.nseg - 1] + cauda
        self.pal = self._palavras(subst)

    def tw(self, seg, palavra, n=0):
        """Instante em que a palavra (normalizada) é dita no parágrafo seg (n-ésima ocorrência)."""
        hits = [x["s"] for x in self.leg if x["seg"] == seg and norm(x["w"]) == palavra]
        return hits[min(n, len(hits) - 1)] if hits else self.ini[seg]

    def seg(self, t):
        return max([k for k in range(self.nseg) if self.ini[k] - 0.15 <= t] or [0])

    def _palavras(self, subst):
        leg, out, i = self.leg, [], 0
        while i < len(leg):
            for chave, val in subst:
                ps = chave.split(); seq = leg[i:i + len(ps)]
                if len(seq) == len(ps) and all(norm(a["w"]) == b for a, b in zip(seq, ps)):
                    pont = re.sub(r"[\wÀ-ÿ]", "", seq[-1]["w"])
                    out.append({"w": val + pont, "s": seq[0]["s"], "e": seq[-1]["e"]}); i += len(ps); break
            else:
                out.append({"w": leg[i]["w"], "s": leg[i]["s"], "e": leg[i]["e"]}); i += 1
        return out

    def transicao(self, im, t, trocas):
        for k in trocas:
            dd = abs(t - (self.ini[k] - 0.15))
            if dd < 0.15:
                im = Image.blend(im, Image.new("RGB", (W, H), BG), 0.6 * (1 - dd / 0.15))
        return im

    def audio(self, cortes=(), pops=(), riser_ate=None, clima="curioso", vol_trilha=-19):
        import audio as AU
        P = self.pasta; out = f"{P}/audio_mix.wav"
        AU.salvar(f"{P}/efeitos.wav", AU.efeitos(self.dur, cortes=cortes, pops=pops, riser_ate=riser_ate) * 0.25)
        AU.salvar(f"{P}/trilha.wav", AU.trilha(self.dur, clima, entra=0.5, respiros=[c - 0.6 for c in cortes]))
        fl = [f"[0]aresample=44100,{AU.VOZ_FILTRO},aformat=channel_layouts=stereo,apad=pad_dur=2,asplit=2[v][sc]",
              f"[2]volume={vol_trilha}dB[m0];[m0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=350[m]",
              "[v][1][m]amix=inputs=3:normalize=0:duration=shortest,loudnorm=I=-14:TP=-1.5:LRA=11[a]"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{P}/narracao.mp3", "-i", f"{P}/efeitos.wav", "-i", f"{P}/trilha.wav",
                        "-filter_complex", ";".join(fl), "-map", "[a]", "-t", f"{self.dur:.2f}", "-ar", "44100", out], check=True)
        return out

    def rodar(self, quadro, **kw_audio):
        """Sem argumentos: render completo -> final.mp4. Com segundos na linha de comando: salva teste_<s>.png."""
        if len(sys.argv) > 1:
            for s in sys.argv[1:]: quadro(float(s)).save(f"{self.pasta}/teste_{s}.png")
            return
        a = self.audio(**kw_audio)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-i", a, "-vf", "vignette=a=PI/5,noise=alls=3:allf=t+u", "-c:v", "libx264", "-preset", "medium",
                               "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k",
                               "-shortest", "-movflags", "+faststart", f"{self.pasta}/final.mp4"], stdin=subprocess.PIPE)
        for f in range(int(self.dur * FPS)):
            ff.stdin.write(quadro(f / FPS).tobytes())
        ff.stdin.close(); ff.wait()
        print("ok", round(self.dur, 1), "s")

def chip_fonte(im, s):
    if not s: return
    d = ImageDraw.Draw(im); f = fonte(26, "Medium"); w = d.textlength(s, font=f)
    if w > 940: f = fonte(22, "Medium"); w = d.textlength(s, font=f)
    x = (W - w) / 2
    d.rounded_rectangle([x - 22, 1508, x + w + 22, 1556], radius=24, fill=BG2, outline=CINZA2, width=2)
    d.text((x, 1516), s, font=f, fill=CINZA)

def entra(t, t0, d=0.35): return ease((t - t0) / d)

def baloes(im, t, perguntas, y0=520):
    """Balões de comentário que entram em sequência: perguntas = [(texto, instante)]."""
    d = ImageDraw.Draw(im); f = fonte(54, "ExtraBold")
    for k, (s, ts) in enumerate(perguntas):
        if t < ts: continue
        q = entra(t, ts); y = y0 + k * 260 + int(30 * (1 - q))
        w = d.textlength(s, font=f)
        if w > 820: f2 = fonte(44, "ExtraBold"); w = d.textlength(s, font=f2)
        else: f2 = f
        x0 = 110 if k % 2 == 0 else W - 110 - w - 80
        d.rounded_rectangle([x0, y, x0 + w + 80, y + 140], radius=40, fill=(255, 255, 255))
        d.polygon([(x0 + 60, y + 140), (x0 + 110, y + 140), (x0 + 50, y + 190)] if k % 2 == 0 else
                  [(x0 + w + 20, y + 140), (x0 + w - 30, y + 140), (x0 + w + 30, y + 190)], fill=(255, 255, 255))
        d.text((x0 + 40, y + 70), s, font=f2, fill=TINTA, anchor="lm")
