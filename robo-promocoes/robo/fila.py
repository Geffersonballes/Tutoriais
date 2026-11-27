"""Fila manual de produtos (Amazon e outros), lida de uma planilha publicada como CSV.

Planilha (Google Sheets → Arquivo → Compartilhar → Publicar na Web → CSV). Colunas (1ª linha):
  loja | link | nome | preco_de | preco_por | imagem | cupom | conferido_em | ativo
- link: o link de afiliado (Amazon: da barra SiteStripe, com a tag ...-20).
- preco_de / preco_por: como na página (ex.: 129,90). preco_de pode ficar vazio.
- imagem: endereço da imagem do produto (botão direito na foto → copiar endereço da imagem).
- conferido_em: data em que o preço foi conferido (AAAA-MM-DD ou DD/MM/AAAA). Só posta se for HOJE
  (regra da Amazon: não mostrar preço desatualizado).
- ativo: vazio/"sim" = pode postar; "não" = ignora.
Cada linha é postada uma vez (o histórico do robô evita repetir).
"""
import csv
import hashlib
import io
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from . import config


def _preco(texto: str) -> float:
    t = (texto or "").replace("R$", "").strip().replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return 0.0


def _data(texto: str) -> str:
    t = (texto or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(t, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return ""


def ler(texto_csv: str | None = None) -> list[dict]:
    if texto_csv is None:
        if not config.FILA_CSV_URL:
            return []
        resp = requests.get(config.FILA_CSV_URL, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        texto_csv = resp.text
    hoje = datetime.now(ZoneInfo(config.FUSO)).strftime("%Y-%m-%d")
    itens = []
    for l in csv.DictReader(io.StringIO(texto_csv)):
        l = {(k or "").strip().lower(): (v or "").strip() for k, v in l.items()}
        if l.get("ativo", "").lower() in ("não", "nao", "n", "0"):
            continue
        if not l.get("link") or not l.get("nome") or not l.get("imagem"):
            continue
        if _data(l.get("conferido_em", "")) != hoje:
            continue  # preço não conferido hoje
        por, de = _preco(l.get("preco_por")), _preco(l.get("preco_de"))
        if por <= 0:
            continue
        de = de if de > por else por
        itens.append({
            "loja": (l.get("loja") or "manual").lower(),
            "id": "fila:" + hashlib.sha1(l["link"].encode()).hexdigest()[:16],
            "nome": l["nome"], "preco": por, "preco_antigo": de,
            "desconto": round((1 - por / de) * 100) if de > por else 0,
            "imagem": l["imagem"], "link": l["link"], "link_produto": "",
            "nota": 0, "vendas": 0, "comissao": 0, "fim": 0, "cupom": l.get("cupom", ""),
            "manual": True,
        })
    return itens
