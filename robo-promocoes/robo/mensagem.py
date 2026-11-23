"""Monta a legenda no formato dos grupos de achadinhos."""
import random

FRASES = [
    "É melhor ter e não precisar, do que precisar e não ter! ❤️",
    "Corre que esse preço não dura! 🏃‍♀️💨",
    "Achadinho do dia! 😍",
    "Preço de banana! 🍌",
    "Esse eu já colocava no carrinho! 🛒",
    "Baixou MUITO! 📉",
    "Quem viu, viu! 👀",
    "Pra quem estava esperando a promoção! 🙌",
]


def reais(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def montar(oferta: dict, frase: str | None = None) -> str:
    frase = frase or random.choice(FRASES)
    linhas = [frase, "", f"🛍️ {oferta['nome']}", ""]
    if oferta["preco_antigo"] > oferta["preco"]:
        linhas.append(f"de ~{reais(oferta['preco_antigo'])}~")
    linhas.append(f"💥 por *{reais(oferta['preco'])}*")
    linhas += ["", f"🛍️ Compre aqui: {oferta['link']}", "",
               "_Promoção sujeita a alteração de preço e estoque._"]
    return "\n".join(linhas)
