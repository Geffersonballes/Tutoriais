import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "motor"))
from visual import *
OUT = os.path.dirname(os.path.abspath(__file__))
def pal(frase, t0, dur=0.32):
    return [{"w": w, "s": t0 + i * dur, "e": t0 + (i + 1) * dur - 0.04} for i, w in enumerate(frase.split())]

# 1) gancho
im = fundo(); cabecalho(im); d = ImageDraw.Draw(im)
icone_acai(im, W // 2, 560, 1.25)
texto_centro(d, 820, "VENDEU NO iFOOD POR", fonte(46, "SemiBold"), CINZA)
numero_grande(im, 900, 20, 1, BRANCO, 200)
texto_centro(d, 1180, "Quanto fica com você?", fonte(64, "ExtraBold"), AMBAR)
legenda(im, pal("Quanto desse dinheiro fica com quem vendeu?", 0), 1.3)
im.save(f"{OUT}/estilo_1_gancho.png")

# 2) cupom fiscal sendo descontado
linhas = [("AÇAÍ 500 ML", 20, "base"), ("COMISSÃO iFOOD 23%", 4.60, "menos"), ("TAXA PAGTO APP 3,2%", 0.64, "menos"),
          ("POLPA + COMPLEMENTOS*", 7.00, "menos"), ("COPO, TAMPA, SACOLA*", 1.50, "menos"),
          ("MENSALIDADE + DAS / COPO", 0.77, "menos")]
im = fundo(); cabecalho(im); d = ImageDraw.Draw(im)
fim = cupom(im, linhas, 6, y=230)
d.text((110, fim + 60), "SOBRANDO ATÉ AQUI", font=fonte(36, "SemiBold"), fill=CINZA)
d.text((110, fim + 100), brl(5.49), font=fonte(150, "Black"), fill=VERDE)
rodape_fonte(im, "*exemplo de custo · iFood: Plano Entrega, valores divulgados em 2026")
legenda(im, pal("Dividindo por trezentos copos no mês, quase oitenta centavos.", 0), 2.0)
im.save(f"{OUT}/estilo_2_cupom.png")

# 3) comparação
im = fundo(); cabecalho(im); d = ImageDraw.Draw(im)
texto_centro(d, 330, "O MESMO AÇAÍ DE R$ 20", fonte(52, "ExtraBold"), BRANCO)
texto_centro(d, 400, "quanto sobra para quem vende", fonte(38, "Medium"), CINZA)
barras(im, [("iFood (entrega pelo app)", 5.49, VERM), ("Balcão, pago no débito", 10.93, VERDE)], 1, y=560, maxv=11)
texto_centro(d, 1150, "QUASE O DOBRO", fonte(110, "Black"), AMBAR)
rodape_fonte(im, "Antes de luz, aluguel e da sua hora de trabalho")
legenda(im, pal("O mesmo açaí no balcão deixa perto de onze reais.", 0), 2.3)
im.save(f"{OUT}/estilo_3_comparacao.png")
print("ok")
