"""Monta a legenda nos formatos dos grupos de achadinhos.

Formatos (escolhidos pelo robô; cada um vai como subId no link para medir qual vende mais):
  padrao     frase / produto / de-por (-%) / nota e vendas / link        ~60%
  economia   ECONOMIZE R$ X / produto / de-por / link                     ~15%
  atepreco   ACHADINHO ATÉ R$ 10/20/30 / produto / só R$ / link            ~15% (só se couber na faixa)
  pergunta   pergunta / produto / preço / link                            ~10%
  relampago  só quando a oferta termina hoje (dado da API), nunca inventado
Além disso, um "Top 5 de hoje" por dia (ver top_do_dia).
"""
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from . import config, frases

AVISO = "_Promoção sujeita a alteração de preço e estoque._"
PESOS = {"padrao": 60, "economia": 15, "atepreco": 15, "pergunta": 10}
FAIXAS = [10, 20, 30]
MAX_NOME = 80


def reais(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def nome_curto(nome: str, limite: int = MAX_NOME) -> str:
    nome = " ".join(nome.split())
    if len(nome) <= limite:
        return nome
    return nome[:limite].rsplit(" ", 1)[0].rstrip(" ,-|/") + "…"


def vendidos(n: float) -> str:
    n = int(n)
    if n >= 1000:
        mil = n / 1000
        texto = f"{mil:.1f}".replace(".", ",").replace(",0", "") if mil < 10 else str(int(mil))
        return f"+{texto} mil vendidos"
    return f"{n} vendidos"


def faixa(preco: float) -> int | None:
    return next((f for f in FAIXAS if preco <= f), None)


def termina_hoje(oferta: dict) -> bool:
    fim = oferta.get("fim") or 0
    if not fim or fim < time.time():
        return False
    tz = ZoneInfo(config.FUSO)
    return datetime.fromtimestamp(fim, tz).date() == datetime.now(tz).date()


def escolher_formato(oferta: dict) -> str:
    if termina_hoje(oferta):
        return "relampago"
    opcoes = dict(PESOS)
    if faixa(oferta["preco"]) is None:
        opcoes.pop("atepreco")
    if oferta["preco_antigo"] - oferta["preco"] < 5:
        opcoes.pop("economia")
    return random.choices(list(opcoes), weights=list(opcoes.values()))[0]


def _de_por(o: dict, compacto: bool = False) -> list[str]:
    tem_de = o["preco_antigo"] > o["preco"]
    pct = f"  (-{round(o['desconto'])}%)" if o["desconto"] >= 5 else ""
    if compacto:
        return [f"✅ de ~{reais(o['preco_antigo'])}~ por *{reais(o['preco'])}*" if tem_de
                else f"✅ por *{reais(o['preco'])}*"]
    linhas = [f"de ~{reais(o['preco_antigo'])}~"] if tem_de else []
    return linhas + [f"💥 por *{reais(o['preco'])}*{pct}"]


def _prova(o: dict) -> list[str]:
    partes = []
    if o.get("nota", 0) >= 4:
        partes.append(f"⭐ {o['nota']:.1f}".replace(".", ","))
    if o.get("vendas", 0) >= 100:
        partes.append(vendidos(o["vendas"]))
    return [" · ".join(partes)] if partes else []


def montar(o: dict, formato: str = "padrao", frase: str | None = None) -> str:
    nome = f"🛍️ {nome_curto(o['nome'])}"
    link = o["link"]
    if formato == "economia":
        corpo = [f"💸 *ECONOMIZE {reais(o['preco_antigo'] - o['preco'])}*", "", nome,
                 *_de_por(o, compacto=True), "", f"👉 {link}"]
    elif formato == "atepreco":
        corpo = [f"🔥 *ACHADINHO ATÉ {reais(faixa(o['preco']) or o['preco']).replace(',00', '')}* 🔥",
                 "", nome, f"💥 só *{reais(o['preco'])}*", "", f"🛒 {link}"]
    elif formato == "pergunta":
        corpo = [frase or random.choice(frases.PERGUNTA), "", nome,
                 f"💥 *{reais(o['preco'])}*", "", f"🛍️ {link}"]
    elif formato == "relampago":
        hora = datetime.fromtimestamp(o["fim"], ZoneInfo(config.FUSO)).strftime("%Hh%M").replace("h00", "h")
        corpo = [f"⚡ *OFERTA RELÂMPAGO*: acaba hoje às {hora} ⏰", "", nome,
                 *_de_por(o), "", f"🛍️ Compre aqui: {link}"]
    else:
        corpo = [frase or random.choice(frases.PADRAO), "", nome, "", *_de_por(o), *_prova(o),
                 "", f"🛍️ Compre aqui: {link}"]
    return "\n".join(corpo + ["", AVISO])


def top_do_dia(itens: list[dict]) -> str:
    numeros = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    linhas = ["🏆 *TOP 5 ACHADINHOS DE HOJE* 🏆", "Perdeu algum? Corre que ainda dá tempo! 👇", ""]
    for n, i in zip(numeros, itens[:5]):
        linhas += [f"{n} {nome_curto(i['nome'], 45)}: *{reais(i['preco'])}*", f"👉 {i['link']}", ""]
    return "\n".join(linhas + [AVISO])
