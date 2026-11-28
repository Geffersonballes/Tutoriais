# Pasta de modelos (fora do git)

Os pacotes (~104 MB) ficam no `.gitignore`. Para baixar de novo (licenças em `LICENCAS.md`):

```bash
M=tiktok-geopolitica/assets/modelos
# 1) personagens (OpenGameArt, CC0) — só FBX + Preview
mkdir -p $M/quaternius_ultimate_animated_character && cd $M/quaternius_ultimate_animated_character
curl -L -o pacote.zip https://opengameart.org/sites/default/files/ultimate_animated_character_pack_by_quaternius.zip
unzip -q pacote.zip "*/FBX/*" "*/Preview.png" && rm pacote.zip
```

2) e 3) ruas e carros vêm do itch.io (download gratuito, "No thanks, just take me to the downloads"):
- https://quaternius.itch.io/lowpoly-modular-street → `Modular Street Pack by Quaternius.zip` → descompactar em `quaternius_modular_streets/`
- https://quaternius.itch.io/lowpoly-cars → `Realistic Car Pack - Nov 2018.zip` → descompactar em `quaternius_cars/`

Pelo terminal, o itch.io aceita: pegar o `csrf_token` da página, `POST <página>/download_url` (devolve a
página de download com os `data-upload_id`) e `POST <página>/file/<upload_id>?source=view_game&as_props=1`
com o mesmo token (devolve a URL direta do arquivo, válida por 60 s).

Usado por: `tiktok-geopolitica/motor/testes_visual/cena_v3.py`.
