"""Robô de promoções.

Uso:
  python -m robo teste            # busca na Shopee e só IMPRIME as mensagens
  python -m robo teste --exemplo  # usa produtos de exemplo (não precisa de chave)
  python -m robo enviar-teste    # manda 1 mensagem de TESTE (exemplo) só para os GRUPOS do .env
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

from . import config, historico, mensagem, shopee, whatsapp


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
        dados = json.loads((Path(__file__).parent / "exemplo.json").read_text(encoding="utf-8"))
        ofertas = [shopee.normalizar(n) for n in dados]
    else:
        palavra = random.choice(config.SHOPEE_PALAVRAS)
        log(f"Buscando na Shopee: '{palavra}'")
        ofertas = shopee.buscar_ofertas(palavra, pagina=random.randint(1, 3))
    boas = [o for o in ofertas if passa_no_filtro(o) and not historico.ja_postado(o["id"])]
    boas.sort(key=lambda o: (o["desconto"], o["vendas"]), reverse=True)
    log(f"{len(ofertas)} ofertas, {len(boas)} passaram no filtro")
    return boas


def com_link_afiliado(o: dict, exemplo: bool) -> dict:
    if not exemplo:
        o["link"] = shopee.link_curto(o["link_produto"] or o["link"])
    return o


def cmd_teste(args) -> None:
    ofertas = candidatas(args.exemplo)[: args.quantidade]
    if not ofertas:
        print("Nenhuma oferta passou no filtro. Afrouxe DESCONTO_MINIMO / VENDAS_MINIMAS.")
    for o in ofertas:
        o = com_link_afiliado(o, args.exemplo)
        print("\n" + "=" * 50)
        print(f"[imagem] {o['imagem']}")
        print(f"[nota {o['nota']} | vendas {int(o['vendas'])} | comissão {o['comissao']}]")
        print("-" * 50)
        print(mensagem.montar(o))
    print("\n(Modo teste: nada foi enviado ao WhatsApp.)")


IMAGEM_TESTE = "https://placehold.co/600x600/png?text=Teste+do+rob%C3%B4"


def cmd_enviar_teste(args) -> None:
    if not config.GRUPOS:
        sys.exit("Defina GRUPOS no .env (use 'python -m robo grupos' para ver os IDs).")
    dados = json.loads((Path(__file__).parent / "exemplo.json").read_text(encoding="utf-8"))
    o = shopee.normalizar(dados[0])
    texto = "🤖 *TESTE DO ROBÔ* (produto de exemplo, não é oferta real)\n\n" + mensagem.montar(o)
    for grupo in config.GRUPOS:
        whatsapp.enviar_imagem(grupo, IMAGEM_TESTE, texto, mimetype="image/png")
        log(f"Teste enviado para {grupo}")


def cmd_grupos(args) -> None:
    for g in whatsapp.listar_grupos():
        print(f"{g.get('id')}  |  {g.get('subject')}  |  {g.get('size', '?')} pessoas")


def dentro_do_horario() -> bool:
    hora = datetime.now(ZoneInfo(config.FUSO)).hour
    return config.HORA_INICIO <= hora < config.HORA_FIM


def cmd_rodar(args) -> None:
    if not config.GRUPOS:
        sys.exit("Defina GRUPOS no .env (use 'python -m robo grupos' para ver os IDs).")
    log(f"Robô ligado. Grupos: {len(config.GRUPOS)}. Intervalo: {config.INTERVALO_MINUTOS} min.")
    while True:
        espera = config.INTERVALO_MINUTOS * 60
        if not dentro_do_horario():
            log("Fora do horário de postagem; aguardando.")
            time.sleep(600)
            continue
        try:
            ofertas = candidatas()
            if ofertas:
                o = com_link_afiliado(ofertas[0], exemplo=False)
                texto = mensagem.montar(o)
                for grupo in config.GRUPOS:
                    whatsapp.enviar_imagem(grupo, o["imagem"], texto)
                    historico.registrar(o, grupo)
                    log(f"Postado em {grupo}: {o['nome'][:60]}")
                    time.sleep(config.PAUSA_ENTRE_GRUPOS + random.uniform(0, 10))
            else:
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
    sub.add_parser("enviar-teste", help="envia 1 mensagem de teste aos GRUPOS").set_defaults(func=cmd_enviar_teste)
    sub.add_parser("grupos", help="lista os grupos do WhatsApp").set_defaults(func=cmd_grupos)
    sub.add_parser("rodar", help="posta em loop").set_defaults(func=cmd_rodar)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
