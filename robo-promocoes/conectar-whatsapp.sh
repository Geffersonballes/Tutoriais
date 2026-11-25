#!/usr/bin/env bash
# Conecta o chip do robô à Evolution API mostrando o QR Code no próprio terminal.
# Uso:  bash conectar-whatsapp.sh                 (QR Code)
#       bash conectar-whatsapp.sh 5565999998888   (código de 8 letras, sem QR)
set -uo pipefail
cd "$(dirname "$0")"

KEY=$(grep '^EVOLUTION_API_KEY=' .env | cut -d= -f2-)
INST=$(grep '^EVOLUTION_INSTANCIA=' .env | cut -d= -f2-); INST=${INST:-robo}
URL=http://localhost:8080
NUMERO=${1:-}
H=(-H "apikey: $KEY" -H "Content-Type: application/json")
json() { python3 -c "import sys,json
try: d=json.load(sys.stdin)
except Exception: d={}
print($1)"; }

if ! command -v qrencode >/dev/null; then
  echo "Instalando o gerador de QR Code..."
  apt-get update -qq >/dev/null && apt-get install -y -qq qrencode >/dev/null
fi

echo "Esperando a Evolution API responder..."
for _ in $(seq 1 60); do curl -sf "$URL" >/dev/null && break; sleep 2; done

curl -s -X POST "$URL/instance/create" "${H[@]}" \
  -d "{\"instanceName\":\"$INST\",\"integration\":\"WHATSAPP-BAILEYS\",\"qrcode\":true}" >/dev/null

for tentativa in $(seq 1 12); do
  estado=$(curl -s "$URL/instance/connectionState/$INST" "${H[@]}" | json 'd.get("instance",{}).get("state","")')
  if [ "$estado" = "open" ]; then
    echo; echo "✅ WhatsApp do robô CONECTADO (instância: $INST)."; exit 0
  fi
  resp=$(curl -s "$URL/instance/connect/$INST${NUMERO:+?number=$NUMERO}" "${H[@]}")
  clear
  if [ -n "$NUMERO" ]; then
    codigo=$(echo "$resp" | json 'd.get("pairingCode") or ""')
    echo "CÓDIGO DE CONEXÃO:  $codigo"
    echo
    echo "No celular do ROBÔ: WhatsApp > ⋮ > Dispositivos conectados > Conectar dispositivo"
    echo "> 'Conectar com número de telefone' e digite o código acima."
  else
    codigo=$(echo "$resp" | json 'd.get("code") or ""')
    [ -n "$codigo" ] && qrencode -t ANSIUTF8 -m 2 "$codigo" || echo "(QR ainda não disponível)"
    echo "No celular do ROBÔ: WhatsApp > ⋮ > Dispositivos conectados > Conectar dispositivo"
    echo "e aponte a câmera para o QR acima. Ele se renova a cada 30 s."
  fi
  echo "(tentativa $tentativa de 12 — Ctrl+C para cancelar)"
  sleep 30
done
echo "❌ Não conectou. Rode de novo, ou tente: bash conectar-whatsapp.sh 55DDNUMERO"
exit 1
