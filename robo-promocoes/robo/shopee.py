"""Cliente da Shopee Affiliate Open API (GraphQL).

Assinatura (conferida no código de clientes da API):
    Signature = sha256(AppId + Timestamp + CorpoJSON + Secret) em hex
    Authorization: SHA256 Credential=<AppId>, Timestamp=<ts>, Signature=<sig>
O corpo assinado precisa ser exatamente o texto enviado no POST.
"""
import hashlib
import json
import time

import requests

from . import config

CAMPOS_OFERTA = """
      itemId
      productName
      price
      priceMin
      priceMax
      priceDiscountRate
      imageUrl
      productLink
      offerLink
      ratingStar
      sales
      commissionRate
      shopName
"""

# sortType: 1 relevância, 2 mais vendidos, 3 maior preço, 4 menor preço, 5 maior comissão
ORDENAR_MAIS_VENDIDOS = 2


class ErroShopee(Exception):
    pass


def _chamar(query: str, variaveis: dict | None = None) -> dict:
    if not config.SHOPEE_APP_ID or not config.SHOPEE_SECRET:
        raise ErroShopee("Defina SHOPEE_APP_ID e SHOPEE_SECRET no .env")
    corpo = {"query": query}
    if variaveis:
        corpo["variables"] = variaveis
    texto = json.dumps(corpo, separators=(",", ":"), ensure_ascii=False)
    ts = str(int(time.time()))
    assinatura = hashlib.sha256(
        (config.SHOPEE_APP_ID + ts + texto + config.SHOPEE_SECRET).encode("utf-8")
    ).hexdigest()
    resp = requests.post(
        config.SHOPEE_ENDPOINT,
        data=texto.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": (
                f"SHA256 Credential={config.SHOPEE_APP_ID}, "
                f"Timestamp={ts}, Signature={assinatura}"
            ),
        },
        timeout=20,
    )
    resp.raise_for_status()
    dados = resp.json()
    if dados.get("errors"):
        raise ErroShopee(json.dumps(dados["errors"], ensure_ascii=False))
    return dados["data"]


def buscar_ofertas(palavra: str, pagina: int = 1, limite: int = 50) -> list[dict]:
    query = f"""
    query($kw: String, $page: Int, $limit: Int, $sort: Int) {{
      productOfferV2(keyword: $kw, page: $page, limit: $limit, sortType: $sort) {{
        nodes {{ {CAMPOS_OFERTA} }}
        pageInfo {{ page limit hasNextPage }}
      }}
    }}"""
    dados = _chamar(query, {"kw": palavra, "page": pagina, "limit": limite,
                            "sort": ORDENAR_MAIS_VENDIDOS})
    return [normalizar(n) for n in dados["productOfferV2"]["nodes"]]


def link_curto(url: str) -> str:
    query = """
    mutation($url: String!, $subs: [String]) {
      generateShortLink(input: {originUrl: $url, subIds: $subs}) { shortLink }
    }"""
    dados = _chamar(query, {"url": url, "subs": [config.SHOPEE_SUB_ID]})
    return dados["generateShortLink"]["shortLink"]


def _f(valor, padrao=0.0) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def normalizar(n: dict) -> dict:
    """Converte o nó da API para o formato interno do robô."""
    preco = _f(n.get("priceMin") or n.get("price"))
    desconto = _f(n.get("priceDiscountRate"))
    if 0 < desconto < 1:  # caso a API devolva fração em vez de %
        desconto *= 100
    preco_antigo = round(preco / (1 - desconto / 100), 2) if 0 < desconto < 100 else preco
    return {
        "loja": "shopee",
        "id": f"shopee:{n.get('itemId')}",
        "nome": (n.get("productName") or "").strip(),
        "preco": preco,
        "preco_antigo": preco_antigo,
        "desconto": desconto,
        "imagem": n.get("imageUrl") or "",
        "link": n.get("offerLink") or n.get("productLink") or "",
        "link_produto": n.get("productLink") or "",
        "nota": _f(n.get("ratingStar")),
        "vendas": _f(n.get("sales")),
        "comissao": _f(n.get("commissionRate")),
    }
