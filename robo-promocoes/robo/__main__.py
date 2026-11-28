"""Robô de promoções.

Uso:
  python -m robo teste            # busca na Shopee e só IMPRIME as mensagens
  python -m robo teste --exemplo  # usa produtos de exemplo (não precisa de chave)
  python -m robo formatos        # mostra todos os formatos de mensagem com um produto de exemplo
  python -m robo enviar-teste    # manda 1 mensagem de TESTE (exemplo) só para os GRUPOS do .env
  python -m robo fila            # mostra o que a fila manual (planilha) postaria hoje, sem enviar
  python -m robo postar-agora    # posta 1 oferta DE VERDADE agora (fila primeiro) nos GRUPOS
  python -m robo grupos           # lista os grupos do número do robô (para pegar os IDs)
  python -m robo rodar            # modo de produção: posta nos GRUPOS em loop
"""
import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import config, fila, historico, mensagem, shopee, whatsapp


def log(*a):
    print(datetime.now(ZoneInfo(config.FUSO)).strftime("%d/%m %H:%M:%S"), *a, flush=True)


def passa_no_filtro(o: dict) -> bool:
    return (
        bool(o["nome"]) and bool(o["imagem"]) and bool(o["link_produto"] or o["link"])
        and o["desconto"] >= config.DESCONTO_MINIMO
        and config.PRECO_MINIMO <= o["preco"] <= config.PRECO_MAXIMO
        and (o["nota"] == 0 or o["nota"] >= config.NOTA_MINIMA)
        and o["vendas"] >= config.VENDAS_MINIMAS
    )


def candidatas(exemplo: bool = False) -> list[dict]:
    if exemplo:
        ofertas = exemplos()
    else:
        palavra = random.choice(config.SHOPEE_PALAVRAS)
        log(f"Buscando na Shopee: '{palavra}'")
        ofertas = shopee.buscar_ofertas(palavra, pagina=random.randint(1, 3))
    boas = [o for o in ofertas if passa_no_filtro(o) and not historico.ja_postado(o["id"])]
    boas.sort(key=lambda o: (o["desconto"], o["vendas"]), reverse=True)
    log(f"{len(ofertas)} ofertas, {len(boas)} passaram no filtro")
    return boas


def com_link_afiliado(o: dict, exemplo: bool, formato: str = "") -> dict:
    """Gera o link de afiliado com subIds: canal (do .env), formato e um id do post."""
    if not exemplo:
        post = "p" + datetime.now(ZoneInfo(config.FUSO)).strftime("%y%m%d%H%M")
        o["link"] = shopee.link_curto(o["link_produto"] or o["link"], formato, post)
    return o


FORMATOS = ["padrao", "economia", "atepreco", "pergunta", "relampago"]
NOMES = {"padrao": "Padrão", "economia": "Economize R$", "atepreco": "Achadinho até R$",
         "pergunta": "Pergunta", "relampago": "Relâmpago", "top_do_dia": "Top 5 de hoje"}


def exemplos() -> list[dict]:
    dados = json.loads((Path(__file__).parent / "exemplo.json").read_text(encoding="utf-8"))
    return [shopee.normalizar(n) for n in dados]


def cmd_teste(args) -> None:
    ofertas = candidatas(args.exemplo)[: args.quantidade]
    if not ofertas:
        print("Nenhuma oferta passou no filtro. Afrouxe DESCONTO_MINIMO / VENDAS_MINIMAS.")
    for o in ofertas:
        formato = mensagem.escolher_formato(o)
        o = com_link_afiliado(o, args.exemplo, formato)
        print("\n" + "=" * 50)
        print(f"[formato {formato}] [imagem] {o['imagem']}")
        print(f"[nota {o['nota']} | vendas {int(o['vendas'])} | comissão {o['comissao']}]")
        print("-" * 50)
        print(mensagem.montar(o, formato))
    print("\n(Modo teste: nada foi enviado ao WhatsApp.)")


IMAGEM_TESTE = "https://placehold.co/600x600/png?text=Teste+do+rob%C3%B4"


def textos_de_exemplo() -> list[tuple[str, str]]:
    o = exemplos()[0]
    relampago = dict(o, fim=int(datetime.now(ZoneInfo(config.FUSO)).replace(
        hour=23, minute=0, second=0).timestamp()))
    barato = dict(exemplos()[0], nome="Organizador de Gaveta Ajustável Kit 6 Peças",
                  preco=17.9, preco_antigo=39.9, desconto=55)
    textos = [(f, mensagem.montar(relampago if f == "relampago" else barato if f == "atepreco" else o, f))
              for f in FORMATOS]
    itens = [dict(x, link=x["link"]) for x in exemplos()[:2]] + [barato]
    return textos + [("top_do_dia", mensagem.top_do_dia(itens))]


def conferir_grupos() -> None:
    """Para se o número do robô não participa de algum grupo do .env (o envio 'daria certo' mas não chegaria)."""
    ids = {g.get("id") for g in whatsapp.listar_grupos()}
    fora = [g for g in config.GRUPOS if g not in ids]
    if fora:
        sys.exit("O número do robô NÃO participa destes grupos do .env: " + ", ".join(fora)
                 + "\nAdicione o robô ao grupo (como admin) ou corrija GRUPOS. Veja: python -m robo grupos")


def cmd_formatos(args) -> None:
    for nome, texto in textos_de_exemplo():
        print("\n" + "=" * 20 + f" {nome} " + "=" * 20)
        print(texto)


def cmd_enviar_teste(args) -> None:
    if not config.GRUPOS:
        sys.exit("Defina GRUPOS no .env (use 'python -m robo grupos' para ver os IDs).")
    conferir_grupos()
    textos = textos_de_exemplo()
    if args.formato != "todos":
        textos = [t for t in textos if t[0] == args.formato]
    for grupo in config.GRUPOS:
        for nome, texto in textos:
            texto = f"🤖 *TESTE DO ROBÔ* · formato _{NOMES.get(nome, nome)}_ (exemplo, não é oferta real)\n\n" + texto
            if nome == "top_do_dia":
                whatsapp.enviar_texto(grupo, texto)
            else:
                whatsapp.enviar_imagem(grupo, IMAGEM_TESTE, texto, mimetype="image/png")
            log(f"Teste '{nome}' enviado para {grupo}")
            time.sleep(config.PAUSA_ENTRE_GRUPOS)


def cmd_fila(args) -> None:
    if not config.FILA_CSV_URL:
        sys.exit("FILA_CSV_URL não definido no .env.")
    motivos: list = []
    itens = fila.ler(motivos=motivos)
    for nome, motivo in motivos:
        print(f"ignorado: {nome[:50]}  →  {motivo}")
    print(f"{len(itens)} item(ns) válidos para hoje (preço conferido hoje):")
    for o in itens:
        formato = mensagem.escolher_formato(o)
        status = " (já postado)" if historico.ja_postado(o["id"]) else ""
        print("\n" + "=" * 50 + f"\n[{o['loja']} · formato {formato}]{status} [imagem] {o['imagem']}\n" + "-" * 50)
        print(mensagem.montar(o, formato))


def cmd_grupos(args) -> None:
    for g in whatsapp.listar_grupos():
        print(f"{g.get('id')}  |  {g.get('subject')}  |  {g.get('size', '?')} pessoas")


def dentro_do_horario() -> bool:
    hora = datetime.now(ZoneInfo(config.FUSO)).hour
    return config.HORA_INICIO <= hora < config.HORA_FIM


def postar_top_se_for_hora() -> None:
    if not config.HORA_TOP:
        return
    tz = ZoneInfo(config.FUSO)
    agora = datetime.now(tz)
    if agora.hour < config.HORA_TOP:
        return
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    for grupo in config.GRUPOS:
        hoje = historico.postados_desde(inicio, grupo)
        if any(p["id"].startswith("top:") for p in hoje):
            continue
        itens = [p for p in hoje if not p["id"].startswith("top:")]
        if len(itens) < 3:
            continue
        itens = list({p["id"]: p for p in itens}.values())[-5:]
        whatsapp.enviar_texto(grupo, mensagem.top_do_dia(itens))
        historico.registrar({"id": f"top:{agora:%Y-%m-%d}", "nome": "Top do dia", "preco": 0,
                             "link": ""}, grupo, "top_do_dia")
        log(f"Top do dia postado em {grupo}")


def postar_uma() -> bool:
    """Posta a próxima oferta (fila manual primeiro, depois Shopee) em todos os GRUPOS."""
    ofertas = [o for o in fila.ler() if not historico.ja_postado(o["id"])]
    if ofertas:
        log(f"Fila manual: {len(ofertas)} item(ns) para hoje")
    elif config.SHOPEE_APP_ID:
        ofertas = candidatas()
    if not ofertas:
        log("Nada para postar agora.")
        return False
    formato = mensagem.escolher_formato(ofertas[0])
    o = ofertas[0] if ofertas[0].get("manual") else \
        com_link_afiliado(ofertas[0], exemplo=False, formato=formato)
    texto = mensagem.montar(o, formato)
    for grupo in config.GRUPOS:
        whatsapp.enviar_imagem(grupo, o["imagem"], texto)
        historico.registrar(o, grupo, formato)
        log(f"Postado em {grupo} [{formato}]: {o['nome'][:60]}")
        time.sleep(config.PAUSA_ENTRE_GRUPOS + random.uniform(0, 10))
    return True


def cmd_postar_agora(args) -> None:
    if not config.GRUPOS:
        sys.exit("Defina GRUPOS no .env.")
    conferir_grupos()
    postar_uma()


def cmd_rodar(args) -> None:
    if not config.GRUPOS:
        sys.exit("Defina GRUPOS no .env (use 'python -m robo grupos' para ver os IDs).")
    conferir_grupos()
    log(f"Robô ligado. Grupos: {len(config.GRUPOS)}. Intervalo: {config.INTERVALO_MINUTOS} min.")
    while True:
        espera = config.INTERVALO_MINUTOS * 60
        if not dentro_do_horario():
            log("Fora do horário de postagem; aguardando.")
            time.sleep(600)
            continue
        try:
            postar_top_se_for_hora()
            if not postar_uma():
                espera = 120  # tenta outra palavra logo
        except Exception as e:  # noqa: BLE001 - o robô não pode parar por um erro
            log(f"ERRO: {e}")
            espera = 300
        # variação aleatória para não postar em ritmo de máquina
        time.sleep(espera + random.uniform(-60, 120))


def main() -> None:
    p = argparse.ArgumentParser(prog="robo")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("teste", help="mostra as mensagens sem enviar")
    t.add_argument("--exemplo", action="store_true", help="usa produtos de exemplo")
    t.add_argument("--quantidade", type=int, default=5)
    t.set_defaults(func=cmd_teste)
    sub.add_parser("fila", help="mostra a fila manual de hoje").set_defaults(func=cmd_fila)
    sub.add_parser("postar-agora", help="posta 1 oferta de verdade agora").set_defaults(func=cmd_postar_agora)
    sub.add_parser("formatos", help="mostra todos os formatos").set_defaults(func=cmd_formatos)
    e = sub.add_parser("enviar-teste", help="envia mensagem(ns) de teste aos GRUPOS")
    e.add_argument("--formato", default="padrao", choices=FORMATOS + ["top_do_dia", "todos"])
    e.set_defaults(func=cmd_enviar_teste)
    sub.add_parser("grupos", help="lista os grupos do WhatsApp").set_defaults(func=cmd_grupos)
    sub.add_parser("rodar", help="posta em loop").set_defaults(func=cmd_rodar)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
