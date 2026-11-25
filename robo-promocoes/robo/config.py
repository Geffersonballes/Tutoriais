"""Configuração lida de variáveis de ambiente (ou do arquivo .env)."""
import os
from pathlib import Path


def _carregar_env(caminho: Path) -> None:
    """Carrega um .env simples (CHAVE=valor) sem sobrescrever o que já existe."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_env(Path(__file__).resolve().parent.parent / ".env")


def _lista(nome: str) -> list[str]:
    return [x.strip() for x in os.getenv(nome, "").split(",") if x.strip()]


def _num(nome: str, padrao: float) -> float:
    valor = os.getenv(nome, "").strip()
    return float(valor) if valor else padrao


# Shopee Affiliate Open API
SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID", "")
SHOPEE_SECRET = os.getenv("SHOPEE_SECRET", "")
SHOPEE_ENDPOINT = os.getenv("SHOPEE_ENDPOINT", "https://open-api.affiliate.shopee.com.br/graphql")
SHOPEE_PALAVRAS = _lista("SHOPEE_PALAVRAS") or ["achadinhos", "casa", "cozinha", "beleza", "eletronicos"]
SHOPEE_SUB_ID = os.getenv("SHOPEE_SUB_ID", "whatsapp")

# Evolution API (WhatsApp)
EVOLUTION_URL = os.getenv("EVOLUTION_URL", "http://localhost:8080").rstrip("/")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCIA = os.getenv("EVOLUTION_INSTANCIA", "robo")
GRUPOS = _lista("GRUPOS")  # JIDs, ex.: 1203630xxxxxxxx@g.us

# Filtros
DESCONTO_MINIMO = _num("DESCONTO_MINIMO", 40)       # %
PRECO_MINIMO = _num("PRECO_MINIMO", 10)             # R$
PRECO_MAXIMO = _num("PRECO_MAXIMO", 300)            # R$
NOTA_MINIMA = _num("NOTA_MINIMA", 4.5)
VENDAS_MINIMAS = _num("VENDAS_MINIMAS", 50)

# Cupom (opcional): aparece como "🎟️ Cupom: *TEXTO*" em todas as ofertas até a validade (AAAA-MM-DD).
# Só use cupom real e vigente. Ex.: CUPOM_TEXTO=resgate R$ 20 OFF na página da oferta
CUPOM_TEXTO = os.getenv("CUPOM_TEXTO", "").strip()
CUPOM_VALIDADE = os.getenv("CUPOM_VALIDADE", "").strip()

# Ritmo
INTERVALO_MINUTOS = _num("INTERVALO_MINUTOS", 15)   # entre um post e outro
HORA_INICIO = int(_num("HORA_INICIO", 8))
HORA_FIM = int(_num("HORA_FIM", 23))
FUSO = os.getenv("FUSO", "America/Cuiaba")
HORA_TOP = int(_num("HORA_TOP", 20))                 # "Top 5 de hoje" (0 = desligado)
PAUSA_ENTRE_GRUPOS = _num("PAUSA_ENTRE_GRUPOS", 20)  # segundos
NAO_REPETIR_DIAS = _num("NAO_REPETIR_DIAS", 7)

# Banco de histórico
BANCO = os.getenv("BANCO", str(Path(__file__).resolve().parent.parent / "dados" / "historico.db"))
