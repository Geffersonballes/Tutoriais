"""Gera kwai/Kwai_postagens.docx (e .txt) a partir de kwai/fila.json: link do vídeo + título + legenda adaptada ao Kwai."""
import json, re, os, docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIRA = {"#fyp", "#foryou", "#tiktokbrasil", "#shorts", "#aprendanotiktok", "#gamesnotiktok", "#tiktoklive", "#viral", "#paravoce"}
def legenda(pasta):
    t = open(os.path.join(R, pasta, "legenda_post.txt"), encoding="utf-8").read()
    t = re.sub(r"(?m)^(Título|Produto Kwai Shop).*$", "", t).strip()
    corpo, tags = [], []
    for linha in t.splitlines():
        if linha.strip().startswith("#"): tags += [h for h in linha.split() if h.lower() not in TIRA]
        elif linha.strip(): corpo.append(linha.strip())
    return " ".join(corpo), " ".join(dict.fromkeys(["#kwai", "#kwaibrasil", "#paravoce"] + tags + ["#pecaporpeca"]))
def link(par, url, texto):
    r_id = par.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r"); rp = OxmlElement("w:rPr"); u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rp.append(u)
    c = OxmlElement("w:color"); c.set(qn("w:val"), "1F5FD1"); rp.append(c); r.append(rp)
    tx = OxmlElement("w:t"); tx.text = texto; r.append(tx); h.append(r); par._p.append(h)
fila = json.load(open(os.path.join(R, "kwai", "fila.json"), encoding="utf-8"))
d = docx.Document(); d.add_heading("Kwai — Peça por Peça: vídeos para postar", 0)
d.add_paragraph("Como usar: toque em \"Baixar vídeo\", salve no celular, abra o Kwai, escolha o vídeo, cole a legenda e poste (ou agende). Poste na ordem, 3 a 5 por dia, com pelo menos 1h30 entre eles. Se o Kwai mostrar a opção de marcar \"conteúdo gerado por IA\", ligue. Os vídeos novos entram no fim desta lista todo dia.")
txt = []
for i, item in enumerate(fila, 1):
    serie, titulo, pasta, url = item[:4]; prod = item[4] if len(item) > 4 else ""
    corpo, tags = legenda(pasta)
    d.add_heading(f"{i:02d}. {titulo}  ({serie})", 2)
    p = d.add_paragraph(); link(p, url, "▶ Baixar vídeo")
    if prod: d.add_paragraph(f"🛒 Produto sugerido (Kwai Shop): {prod}")
    d.add_paragraph("Legenda (copie tudo):"); d.add_paragraph(f"{corpo}\n\n{tags}")
    txt.append(f"{i:02d}. {titulo} ({serie})\nVídeo: {url}\n" + (f"🛒 Produto sugerido (Kwai Shop): {prod}\n" if prod else "") + f"Legenda:\n{corpo}\n\n{tags}\n")
d.save(os.path.join(R, "kwai", "Kwai_postagens.docx"))
CAB = open(os.path.join(R, "kwai", "cabecalho.txt"), encoding="utf-8").read()
open(os.path.join(R, "kwai", "Kwai_postagens.txt"), "w", encoding="utf-8").write(CAB + "\n-------------------------------------\n\n".join(txt))
print(len(fila), "vídeos")
