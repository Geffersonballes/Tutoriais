"""Texto da capa do Facebook sobre o render 3D. Uso: python3 capa_facebook_texto.py"""
import os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__))
FONTS = "/home/user/Tutoriais/tiktok-geopolitica/assets/fonts"
def fonte(tam, peso):
    f = ImageFont.truetype(os.path.join(FONTS, "Montserrat[wght].ttf"), tam); f.set_variation_by_axes([peso]); return f
im = Image.open(os.path.join(D, "capa_facebook_3d.jpg")).convert("RGB"); d = ImageDraw.Draw(im)
CX = 790  # centro do texto (fica dentro do recorte do celular)
def linha(txt, y, f, cor, sombra=6):
    w = d.textlength(txt, font=f); x = CX - w / 2
    d.text((x + sombra, y + sombra), txt, font=f, fill=(10, 30, 90))
    d.text((x, y), txt, font=f, fill=cor, stroke_width=0)
linha("Como isso funciona? Eu explico.", 92, fonte(40, 700), (255, 255, 255), 3)
linha("PEÇA POR", 175, fonte(110, 900), (255, 255, 255))
linha("PEÇA", 290, fonte(110, 900), (255, 214, 10))
# pílula
txt = "GAMES  •  GEOPOLÍTICA  •  EM 3D"; f = fonte(30, 800); w = d.textlength(txt, font=f)
d.rounded_rectangle((CX - w / 2 - 26, 425, CX + w / 2 + 26, 477), radius=26, fill=(255, 255, 255))
d.text((CX - w / 2, 433), txt, font=f, fill=(25, 60, 160))
im.save(os.path.join(D, "capa_facebook.jpg"), quality=95)
